import time
from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from rich.progress import TaskID

from cs2_storage_unit_tracker.api.frankfurter import FrankfurterApiClient
from cs2_storage_unit_tracker.api.steam import SteamApiClient
from cs2_storage_unit_tracker.cli.content.rich import components_key, messages_key
from cs2_storage_unit_tracker.cli.renderers.rich import RichMessageRenderer
from cs2_storage_unit_tracker.cli.renderers.rich.component_renderer import (
    RichComponentRenderer,
)
from cs2_storage_unit_tracker.config import STEAM_API_CONFIG
from cs2_storage_unit_tracker.config.loaders import FileLoader
from cs2_storage_unit_tracker.config.models import (
    Portfolio,
    Runtime,
    SyncStatus,
    UserSettings,
)
from cs2_storage_unit_tracker.config.models.portfolio_model import Item
from cs2_storage_unit_tracker.formatting.currency import CurrencyFormatter
from cs2_storage_unit_tracker.helpers.errors import ApiError
from cs2_storage_unit_tracker.helpers.status_data import (
    ProgressCounters,
    calculate_item,
    calculate_report,
)


@dataclass(frozen=True, slots=True)
class App:
    file_loader: FileLoader
    portfolio: Portfolio
    runtime: Runtime
    sync_status: SyncStatus
    user_settings: UserSettings
    steam_api_client: SteamApiClient
    exchange_api_client: FrankfurterApiClient
    currency_formatter: CurrencyFormatter
    message_renderer: RichMessageRenderer
    live_component_renderer: Callable[[], AbstractContextManager[RichComponentRenderer]]

    def run(self) -> None:
        source_currency: str = self.user_settings.steam_api.currency

        if not self._prepare_run_state(source_currency=source_currency):
            return

        self.runtime.reset_requests_if_new_day()
        self._persist_state()

        requests_left: int = (
            STEAM_API_CONFIG.request_limit_per_day - self.runtime.total_requests
        )
        if requests_left <= 0:
            self.message_renderer.print(
                key=messages_key.DAILY_LIMIT,
                variables={"limit": STEAM_API_CONFIG.request_limit_per_day},
            )
            return

        total_items: Mapping[str, Item] = self.portfolio.root
        outdated_items: tuple[tuple[str, Item], ...] = tuple(
            (name, item)
            for name, item in total_items.items()
            if name not in self.sync_status.synced_items
        )

        counters = ProgressCounters(
            pending=len(outdated_items),
            outdated_total=len(outdated_items),
            total_items_count=len(total_items),
            successful=len(self.sync_status.synced_items),
        )

        if not self._confirm_partial_run(
            counters=counters, requests_left=requests_left
        ):
            return

        rate, should_continue = self._resolve_exchange_rate(
            source_currency=source_currency
        )
        if not should_continue:
            return

        self._run_sync_loop(outdated_items=outdated_items, counters=counters, rate=rate)

    def _clear_sync_state(self) -> None:
        self.sync_status.synced_items.clear()
        self.runtime.reset()

    def _persist_state(self) -> None:
        self.file_loader.save_runtime(self.runtime)
        self.file_loader.save_sync_status(self.sync_status)

    def _prepare_run_state(self, source_currency: str) -> bool:
        last_source_currency: str = self.runtime.last_source_currency
        should_reset = True

        if self.runtime.was_run_recently():
            key: messages_key = (
                messages_key.ALREADY_FINISHED
                if self.runtime.finished
                else messages_key.ALREADY_RUN
            )
            if not self.message_renderer.confirm(key=key):
                return False
            should_reset: bool = self.runtime.finished

        if should_reset:
            self._clear_sync_state()
        elif last_source_currency != source_currency:
            try:
                exchange_rate: Decimal = self.exchange_api_client.get_rate(
                    source_currency=last_source_currency,
                    target_currency=source_currency,
                )
                self.runtime.exchange_money_values(exchange_rate=exchange_rate)
                self.runtime.last_source_currency = source_currency
            except ApiError:
                if not self.message_renderer.confirm(
                    key=messages_key.LAST_CURRENCY_EXCHANGE_FAIL
                ):
                    return False
                self._clear_sync_state()

        return True

    def _confirm_partial_run(
        self, counters: ProgressCounters, requests_left: int
    ) -> bool:
        missing_requests = max(0, counters.outdated_total - requests_left)
        if missing_requests <= 0:
            return True

        completable_requests = counters.outdated_total - missing_requests
        return self.message_renderer.confirm(
            key=messages_key.PARTIAL_RUN,
            variables={
                "completable_requests": completable_requests,
                "outdated_total": counters.outdated_total,
            },
        )

    def _resolve_exchange_rate(
        self, source_currency: str
    ) -> tuple[Decimal | None, bool]:
        if self.user_settings.frankfurter_api.to_currency is None:
            return None, True

        try:
            rate = self.exchange_api_client.get_rate(source_currency=source_currency)
            return rate, True
        except ApiError:
            should_continue = self.message_renderer.confirm(
                key=messages_key.RATE_EXCHANGE_FAIL
            )
            return None, should_continue

    def _run_sync_loop(
        self,
        outdated_items: tuple[tuple[str, Item], ...],
        counters: ProgressCounters,
        rate: Decimal | None,
    ) -> None:
        with self.live_component_renderer() as component_renderer:
            task_id: TaskID = component_renderer.progress_add_task(
                key=components_key.ADD_TASK
            )
            try:
                for item_name, item_details in component_renderer.progress_track_task(
                    outdated_items=outdated_items, task_id=task_id
                ):
                    self._process_item(
                        component_renderer=component_renderer,
                        task_id=task_id,
                        item_name=item_name,
                        item_details=item_details,
                        counters=counters,
                        rate=rate,
                    )

                self.runtime.finished = True
                self._persist_state()
                component_renderer.progress_advance_task(task_id=task_id)
                self._emit_report(
                    component_renderer=component_renderer, counters=counters, rate=rate
                )

            except KeyboardInterrupt:
                self.message_renderer.print(key=messages_key.INTERRUPTED_PROGRAM)
                self._persist_state()
                if counters.pending < counters.outdated_total:
                    self._emit_report(
                        component_renderer=component_renderer,
                        counters=counters,
                        rate=rate,
                    )

    def _process_item(
        self,
        component_renderer: RichComponentRenderer,
        task_id: TaskID,
        item_name: str,
        item_details: Item,
        counters: ProgressCounters,
        rate: Decimal | None,
    ) -> None:
        counters.pending -= 1

        try:
            item_selling_price: Decimal = self.steam_api_client.get_price(
                item_url=item_details.link
            )
        except ApiError:
            self.runtime.total_requests += 1
            counters.failed += 1
            item: dict[str, Any] = calculate_item(
                **counters.as_kwargs(),
                item_name=item_name,
                item_details=item_details,
                item_selling_price=Decimal(0),
                exchange_rate=rate,
                currency_formatter=self.currency_formatter,
            )
            component_renderer.status_update(
                key=components_key.ITEM_FAILED, variables=item["display"]
            )
            component_renderer.progress_advance_task(task_id=task_id)
            time.sleep(STEAM_API_CONFIG.request_interval)
            return

        counters.successful += 1
        item = calculate_item(
            **counters.as_kwargs(),
            item_name=item_name,
            item_details=item_details,
            item_selling_price=item_selling_price,
            exchange_rate=rate,
            currency_formatter=self.currency_formatter,
        )
        item_display: dict[str, Any] = item["display"]
        item_values: dict[str, Any] = item["values"]

        self.runtime.total_units += item_values["units"]
        self.runtime.total_cost += item_values["cost"]
        self.runtime.total_price += item_values["price"]
        self.sync_status.synced_items.add(item_name)
        self.runtime.total_requests += 1

        key: components_key = (
            components_key.ITEM_POSITIVE
            if item_values["profit"] > 0
            else components_key.ITEM_NEGATIVE
        )
        component_renderer.status_update(key=key, variables=item_display)
        component_renderer.progress_advance_task(task_id=task_id)
        time.sleep(STEAM_API_CONFIG.request_interval)

    def _emit_report(
        self,
        component_renderer: RichComponentRenderer,
        counters: ProgressCounters,
        rate: Decimal | None,
    ) -> None:
        report: dict[str, Any] = calculate_report(
            **counters.as_kwargs(),
            total_units=self.runtime.total_units,
            total_cost=self.runtime.total_cost,
            total_price=self.runtime.total_price,
            exchange_rate=rate,
            currency_formatter=self.currency_formatter,
        )
        report_values: dict[str, Any] = report["values"]
        report_display: dict[str, Any] = report["display"]

        if report_values["price"] == 0:
            key: components_key = components_key.REPORT_FAILED
        elif report_values["profit"] > 0:
            key = components_key.REPORT_POSITIVE
        else:
            key = components_key.REPORT_NEGATIVE

        component_renderer.status_update(key=key, variables=report_display)
