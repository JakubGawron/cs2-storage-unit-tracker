from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

from cs2_storage_unit_tracker.api import (
    ApiClient,
    create_frankfurter_api_client,
    create_steam_api_client,
)
from cs2_storage_unit_tracker.api.frankfurter import FrankfurterApiClient
from cs2_storage_unit_tracker.api.steam import SteamApiClient
from cs2_storage_unit_tracker.cli import App
from cs2_storage_unit_tracker.cli.renderers.rich import (
    RichMessageRenderer,
    rich_live_component_renderer,
)
from cs2_storage_unit_tracker.cli.renderers.rich.component_renderer import (
    RichComponentRenderer,
)
from cs2_storage_unit_tracker.config import (
    FRANKFURTER_API_CONFIG,
    STEAM_API_CONFIG,
    Paths,
)
from cs2_storage_unit_tracker.config.loaders import FileLoader
from cs2_storage_unit_tracker.config.models.portfolio_model import Portfolio
from cs2_storage_unit_tracker.config.models.runtime_model import Runtime
from cs2_storage_unit_tracker.config.models.sync_status_model import SyncStatus
from cs2_storage_unit_tracker.config.models.user_settings_model import (
    FrankfurterApiSettings,
    GeneralSettings,
    SteamApiSettings,
    UserSettings,
)
from cs2_storage_unit_tracker.formatting import create_currency_formatter
from cs2_storage_unit_tracker.formatting.currency import CurrencyFormatter


def create_app() -> App:
    PROJECT_DIR: Path = Path(__file__).resolve().parents[1]
    ROOT_DIR: Path = PROJECT_DIR.parents[1]

    paths = Paths(root_dir=ROOT_DIR, project_dir=PROJECT_DIR)
    file_loader = FileLoader(paths=paths)

    portfolio: Portfolio = file_loader.load_portfolio()
    sync_status: SyncStatus = file_loader.load_sync_status()
    user_settings: UserSettings = file_loader.load_user_settings(
        context={
            "steam_api_allowed_currencies": STEAM_API_CONFIG.currencies,
            "frankfurter_api_allowed_currencies": FRANKFURTER_API_CONFIG.currencies,
        }
    )

    api_client = ApiClient()
    steam_api_settings: SteamApiSettings = user_settings.steam_api
    source_currency: str = steam_api_settings.currency

    general_settings: GeneralSettings = user_settings.general
    reset_after_hours: int = general_settings.reset_after_hours
    runtime: Runtime = file_loader.load_runtime(
        context={
            "source_currency": source_currency,
            "reset_after_hours": reset_after_hours,
        }
    )
    frankfurter_api_settings: FrankfurterApiSettings = user_settings.frankfurter_api
    exchanged_currency: str | None = frankfurter_api_settings.to_currency

    steam_api_client: SteamApiClient = create_steam_api_client(
        steam_api_settings=steam_api_settings,
        api_client=api_client,
    )
    frankfurter_api_client: FrankfurterApiClient = create_frankfurter_api_client(
        frankfurter_api_settings=frankfurter_api_settings,
        api_client=api_client,
    )

    currency_formatter: CurrencyFormatter = create_currency_formatter(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        formatting_settings=user_settings.formatting,
    )

    rich_message_renderer = RichMessageRenderer()
    rich_component_renderer: Callable[
        [], AbstractContextManager[RichComponentRenderer]
    ] = rich_live_component_renderer

    return App(
        file_loader=file_loader,
        portfolio=portfolio,
        runtime=runtime,
        sync_status=sync_status,
        user_settings=user_settings,
        steam_api_client=steam_api_client,
        exchange_api_client=frankfurter_api_client,
        currency_formatter=currency_formatter,
        message_renderer=rich_message_renderer,
        live_component_renderer=rich_component_renderer,
    )
