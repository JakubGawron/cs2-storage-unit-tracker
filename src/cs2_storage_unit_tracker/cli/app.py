"""CLI application and state management for Steam inventory synchronization.

This module provides the primary application class (`App`) that orchestrates
the synchronization workflow, including state validation, API interactions,
progress tracking, and report generation.

The `App` class uses dependency injection to manage all collaborators: file
persistence, API clients, renderers, and state models. It implements the
synchronization loop with interrupt handling, currency exchange, and
comprehensive error reporting.
"""

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
from cs2_storage_unit_tracker.cli.renderers.txt import TextDocument
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
    """Main CLI application for Steam inventory price synchronization.

    This class orchestrates the entire synchronization workflow: state
    validation, API interactions, progress tracking, and report generation.
    All dependencies are injected at construction time for testability and
    flexibility.

    Attributes:
        file_loader: Handles TOML-based configuration and state persistence.
        portfolio: In-memory inventory model containing items and metadata.
        runtime: Tracks runtime state (requests, totals, currency, timestamps).
        sync_status: Tracks synced items and synchronization metadata.
        user_settings: User preferences (currencies, API keys, formatting).
        text_document: Text document for timestamped text reports.
        steam_api_client: Steam Community Market API client.
        exchange_api_client: Frankfurter currency exchange API client.
        currency_formatter: Formats monetary values with locale-aware symbols.
        message_renderer: Renders console messages and confirmations.
        live_component_renderer: Factory function for live progress/status
            rendering context manager.
    """

    file_loader: FileLoader
    portfolio: Portfolio
    runtime: Runtime
    sync_status: SyncStatus
    user_settings: UserSettings
    text_document: TextDocument
    steam_api_client: SteamApiClient
    exchange_api_client: FrankfurterApiClient
    currency_formatter: CurrencyFormatter
    message_renderer: RichMessageRenderer
    live_component_renderer: Callable[[], AbstractContextManager[RichComponentRenderer]]

    def run(self) -> None:
        """Execute the main synchronization workflow.

        Orchestrates the complete synchronization process:
        1. Validates run state and handles prior runs, currency changes
        2. Resets daily request counters if needed
        3. Checks API rate limits
        4. Obtains exchange rate if currency conversion is enabled
        5. Executes sync loop for all outdated items
        6. Emits final report

        Returns early (with user notification) if:
        - Daily request limit is exhausted
        - User declines to continue on prompt
        - Exchange rate resolution fails
        """
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

        rate: Decimal | None
        should_continue: bool
        rate, should_continue = self._resolve_exchange_rate(
            source_currency=source_currency
        )
        if not should_continue:
            return

        self._run_sync_loop(outdated_items=outdated_items, counters=counters, rate=rate)

    def _clear_sync_state(self) -> None:
        """Clear all synchronization history and reset runtime state.

        Clears synced item tracking, text document content, and runtime
        counters. Used when starting fresh or resolving currency mismatches.
        """
        self.sync_status.synced_items.clear()
        self.runtime.reset()
        self.text_document.clear()

    def _persist_state(self) -> None:
        """Save runtime and sync status to persistent storage.

        Writes current `Runtime` and `SyncStatus` state to TOML files via
        the `FileLoader`. Called after state initialization and after the
        sync loop completes.
        """
        self.file_loader.save_runtime(self.runtime)
        self.file_loader.save_sync_status(self.sync_status)

    def _prepare_run_state(self, source_currency: str) -> bool:
        """Validate and prepare state before synchronization begins.

        Handles:
        - Recent run detection: prompts user if run was very recent
        - Currency mismatch: converts money values or prompts reset
        - Sync state reset when appropriate

        Args:
            source_currency: The currency configured in user settings.

        Returns:
            `True` if preparation succeeded and sync should proceed;
            `False` if user cancelled or preparation failed.
        """
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
            except ApiError:
                if not self.message_renderer.confirm(
                    key=messages_key.LAST_CURRENCY_EXCHANGE_FAIL
                ):
                    return False
                self._clear_sync_state()

        self.runtime.last_source_currency = source_currency
        return True

    def _confirm_partial_run(
        self, counters: ProgressCounters, requests_left: int
    ) -> bool:
        """Confirm if user accepts partial synchronization due to rate limits.

        Calculates how many items can be synced with remaining API requests.
        If all outdated items fit within the quota, returns `True` without
        prompting. Otherwise, prompts the user to confirm partial completion.

        Args:
            counters: Tracks outdated items, successful, failed, and pending.
            requests_left: Number of API requests remaining for the day.

        Returns:
            `True` if user accepts the partial run or all items fit;
            `False` if user declines.
        """
        missing_requests: int = max(0, counters.outdated_total - requests_left)
        if missing_requests <= 0:
            return True

        completable_requests: int = counters.outdated_total - missing_requests
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
        """Fetch currency exchange rate if conversion is configured.

        Queries the Frankfurter API to convert from `source_currency` to
        the target currency specified in user settings. If no target
        currency is configured, returns `(None, True)` without API calls.

        Args:
            source_currency: The base currency (from Steam API settings).

        Returns:
            A tuple of `(exchange_rate, should_continue)`:
            - `exchange_rate`: The conversion rate, or `None` if no
              conversion is needed.
            - `should_continue`: `True` if sync should proceed; `False`
              if an API error occurred and user declined to continue.

        Raises:
            No exceptions are raised; `ApiError` is caught and user is
            prompted to decide whether to continue without exchange rates.
        """
        if self.user_settings.frankfurter_api.to_currency is None:
            return None, True

        try:
            rate: Decimal = self.exchange_api_client.get_rate(
                source_currency=source_currency
            )
            return rate, True
        except ApiError:
            should_continue: bool = self.message_renderer.confirm(
                key=messages_key.RATE_EXCHANGE_FAIL
            )
            return None, should_continue

    def _run_sync_loop(
        self,
        outdated_items: tuple[tuple[str, Item], ...],
        counters: ProgressCounters,
        rate: Decimal | None,
    ) -> None:
        """Execute the main synchronization loop with live progress tracking.

        Processes each outdated item in sequence, fetching current prices,
        calculating financial metrics, and updating state. Displays real-time
        progress and status in the terminal. Handles `KeyboardInterrupt` by
        gracefully persisting state and emitting a partial report if items
        were processed.

        Args:
            outdated_items: Tuple of (name, Item) pairs for items not yet
                synced in the current run.
            counters: Tracks progress metrics (pending, successful, failed).
            rate: Exchange rate for currency conversion, or `None` if no
                conversion is needed.

        Side Effects:
            - Updates `Runtime`, `SyncStatus`, and `TextDocument`.
            - Persists state to disk on completion or interrupt.
            - Displays real-time progress and final report via component
              renderer and message renderer.
        """
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
        """Process a single item: fetch price, calculate metrics, update state.

        Fetches the current item price from Steam Community Market API,
        calculates financial metrics (cost, profit, ROI, etc.), and updates
        runtime state. Handles API failures gracefully by marking the item
        as failed and continuing. Uses the specified interval between requests
        to respect API rate limits.

        Args:
            component_renderer: Live progress/status renderer.
            task_id: Task ID for progress tracking.
            item_name: Name of the item being processed.
            item_details: Item configuration (purchase cost, quantity, link).
            counters: Tracks progress metrics; updated in-place.
            rate: Exchange rate for currency conversion, or `None`.

        Side Effects:
            - Updates `Runtime` (totals, request count) and `SyncStatus`
              (synced items).
            - Renders status updates to component_renderer.
            - Appends item details to text_document on success.
            - Sleeps for `STEAM_API_CONFIG.request_interval` before returning.
        """
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

        keys: list[components_key] = [
            components_key.ITEM_POSITIVE,
            components_key.TEXT_ITEM_POSITIVE
            if item_values["profit"] > 0
            else components_key.ITEM_NEGATIVE,
            components_key.TEXT_ITEM_NEGATIVE,
        ]
        component_key: components_key = keys[0]
        text_key: components_key = keys[1]
        component_renderer.status_update(key=component_key, variables=item_display)
        self.text_document.add(key=text_key, variables=item_display)
        component_renderer.progress_advance_task(task_id=task_id)
        time.sleep(STEAM_API_CONFIG.request_interval)

    def _emit_report(
        self,
        component_renderer: RichComponentRenderer,
        counters: ProgressCounters,
        rate: Decimal | None,
    ) -> None:
        """Render and persist the final synchronization report.

        Calculates aggregated financial metrics across all processed items,
        determines report status (success, partial, or failure), renders the
        report to the terminal, and persists it to the text document if
        the sync was not a complete failure.

        Report status is determined by:
        - `REPORT_FAILED`: Total selling price is zero (no items synced).
        - `REPORT_POSITIVE`: Total profit is greater than zero.
        - `REPORT_NEGATIVE`: Total profit is zero or negative.

        Args:
            component_renderer: Live status renderer for displaying the report.
            counters: Tracks progress metrics used in aggregated calculations.
            rate: Exchange rate for currency conversion, or `None` if no
                conversion was applied.

        Side Effects:
            - Renders the final report to the terminal via component_renderer.
            - Persists the report to text_document if the sync succeeded
              (i.e., key is not `REPORT_FAILED`).
        """
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

        if key != components_key.REPORT_FAILED:
            self.text_document.save(key=key, variables=report_display)
