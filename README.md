<p align="center">
  <img src="./images/baner.png" alt="cs2-storage-unit-tracker banner" width="100%">
</p>

<h1 align="center">CS2 Storage Unit Tracker</h1>

<p align="center">
  <a href="./README.pl.md">Polska dokumentacja</a>
</p>

<p align="center">
  A CLI application for tracking the market value and profitability of a Steam / CS2 inventory.
</p>

<p align="center">
  <img alt="Python version" src="https://img.shields.io/badge/python-%3E%3D3.14-blue?logo=python&logoColor=white">
  <img alt="Built with uv" src="https://img.shields.io/badge/built%20with-uv-DE5FE9?logo=uv&logoColor=white">
 <img alt="Code style: Ruff" src="https://img.shields.io/badge/code%20style-ruff-black?logo=ruff&logoColor=white">
  <img alt="Version" src="https://img.shields.io/badge/version-1.0.0-informational">
  <img alt="Platform" src="https://img.shields.io/badge/platform-cross--platform-lightgrey">
  <img alt="Status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/license-PolyForm%20Noncommercial%20License%201.0.0-lightgrey">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/JakubGawron/cs2-storage-unit-tracker">
  <img alt="GitHub issues" src="https://img.shields.io/github/issues/JakubGawron/cs2-storage-unit-tracker">
  <img alt="Repo size" src="https://img.shields.io/github/repo-size/JakubGawron/cs2-storage-unit-tracker">
</p>

---

### Trademark Notice

_„Counter-Strike”, „Counter-Strike 2”, and „CS2” are trademarks or registered trademarks of Valve Corporation. This project is independently developed and is not affiliated with, sponsored, authorized, or endorsed by Valve Corporation._

---

## Overview

`cs2-storage-unit-tracker` is a Python CLI application for Steam inventory price synchronization. It tracks items from a Steam inventory / Steam Community Market, retrieves their current market prices, and calculates financial metrics based on the purchase data you configure.

Instead of manually opening Steam Community Market listings, checking prices one by one, calculating the total current value, comparing it against the original purchase cost, and converting between currencies by hand, this application automates that process from the command line.

The main synchronization workflow validates the current state, checks API request limits, determines which items need to be processed, optionally retrieves an exchange rate, fetches Steam prices, calculates financial metrics, updates state, displays live progress, and generates a final report.

### Who this is for

This project is intended for users who:

- own Steam / Counter-Strike 2 items
- want to track their inventory's market value
- want to compare current value against purchase cost
- want to monitor profit or loss
- want to keep historical/report-style results
- prefer a lightweight CLI workflow

---

## Features

- Steam Community Market price synchronization
- Steam / CS2 inventory item tracking
- Configurable item quantities
- Configurable purchase price per item
- Total inventory cost calculation
- Current market value calculation
- Profit calculation
- ROI-related financial calculations
- Optional currency conversion
- Frankfurter exchange-rate integration
- Live CLI progress display
- Persistent synchronization state
- Daily API request tracking
- Partial synchronization when the request quota is insufficient
- Error handling for failed price requests
- Graceful `Ctrl+C` interruption
- Text report generation
- Recent-run handling

---

## How It Works

The application follows this general workflow during a synchronization run:

1. Load and validate the current state.
2. Check whether a recent run requires confirmation/reset behavior.
3. Reset request counters when a new day starts.
4. Determine how many API requests remain available.
5. Determine which configured items still need to be synchronized.
6. Ask for confirmation when only a partial synchronization is possible.
7. Retrieve an exchange rate when currency conversion is enabled.
8. Fetch current Steam Community Market prices.
9. Calculate item-level financial metrics.
10. Update totals and synchronization state.
11. Display live progress in the terminal.
12. Generate the final report.
13. Persist the relevant state.

---

## Requirements

- [Python](https://www.python.org/downloads/) >= 3.14

Runtime dependencies:

- [babel](https://pypi.org/project/Babel/) >= 2.18.0
- [price-parser](https://pypi.org/project/price-parser/) >= 0.5.1
- [pydantic](https://pypi.org/project/pydantic/) >= 2.13.4
- [requests](https://pypi.org/project/requests/) >= 2.34.2
- [rich](https://pypi.org/project/rich/) >= 15.0.0
- [tomli-w](https://pypi.org/project/tomli-w/) >= 1.2.0

---

## Installation & Setup

`cs2-storage-unit-tracker` is distributed as a Python package built with [`uv_build`](https://docs.astral.sh/uv/):

```toml
[build-system]
requires = ["uv_build>=0.12.6,<0.13.0"]
build-backend = "uv_build"
```

You can install and run it using either `uv` (recommended) or standard `pip`.

### Method 1: Using `uv` (Recommended)

`uv` is a fast, modern Python package manager that handles dependencies and virtual environments automatically.

**Install `uv` (If needed)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Clone and setup**

```bash
git clone https://github.com/JakubGawron/cs2-storage-unit-tracker
cd cs2-storage-unit-tracker
```

**Install dependencies**

```bash
uv sync
```

This installs the exact dependency versions pinned in [`uv.lock`](./uv.lock), ensuring a reproducible environment.

**Run the application**

```bash
uv run cs2-storage-unit-tracker
```

**Build the package (Optional)**

```bash
uv build
```

This generates distribution files in the `dist/` directory.

### Method 2: Using Standard Python

**Clone the repository**

```bash
git clone https://github.com/JakubGawron/cs2-storage-unit-tracker
cd cs2-storage-unit-tracker
```

**Create a virtual environment**

```bash
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install the package**

```bash
pip install -e .          # package only
```

Installing with `-e` (editable mode) links to your source directory instead of copying files, so code changes take effect immediately without reinstalling.

> **Note:** This method resolves dependency versions directly from [`pyproject.toml`](./pyproject.toml) and does not use [`uv.lock`](./uv.lock), so installed versions may differ slightly from Method 1.

**Run the application**

```bash
cs2-storage-unit-tracker
```

**Install build tools and build (Optional)**

```bash
pip install build
python -m build
```

---

## Configuration

The project has two main configuration areas:

```text
settings/
├── portfolio.toml
└── settings.toml
```

- [`settings.toml`](./settings/settings.toml) — Steam API, currency conversion, formatting, and general behavior.
- [`portfolio.toml`](./settings/portfolio.toml) — the list of Steam items you own and want to track.

### Settings

[`settings/settings.toml`](./settings/settings.toml)

```toml
[steam_api]

# Steam game app ID to track prices for.
#
# Find app ID at:
# https://steamdb.info/
#
# Default Counter-Strike 2 (app ID: 730)
#
# WARNING: App ID correctness is NOT validated at runtime.
# Invalid app ID may cause failed requests to Steam API.
#
app_id = 730

# Currency used by Steam API when retrieving prices (ISO code).
currency = "USD"


[frankfurter_api]

# Currency to convert prices into (ISO code).
# If empty, currency conversion is disabled.
to_currency = ""


[formatting]

# Controls how currency values are displayed.
#
# true:
# Use locale-aware formatting with localized currency symbols,
# decimal separators, thousands separators, and currency placement.
#
# false:
# Use a consistent format regardless of the user's locale.
#
# Example:
# 1.234,56 €
#
source_currency_use_locale = true
exchanged_currency_use_locale = true


[general]

# Number of hours after which a reset is required.
# Minimum is 6.
reset_after_hours = 24
```

#### `[steam_api]`

| Setting    | Required | Description                                                                                                                                                                                                                                          | Example |
| ---------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `app_id`   | Yes      | Steam game application ID used for price tracking. Default is `730` (Counter-Strike 2). Find app IDs at [SteamDB](https://steamdb.info/). App ID correctness is **not validated at runtime** — an invalid value may cause failed Steam API requests. | `730`   |
| `currency` | Yes      | Currency used by the Steam API when retrieving prices, as an ISO currency code.                                                                                                                                                                      | `"USD"` |

#### `[frankfurter_api]`

| Setting       | Required | Description                                                                                        | Example |
| ------------- | -------- | -------------------------------------------------------------------------------------------------- | ------- |
| `to_currency` | Yes      | Target currency for conversion, as an ISO currency code. Leave empty (`""`) to disable conversion. | `"EUR"` |

```toml
# Enable conversion
to_currency = "EUR"

# Disable conversion
to_currency = ""
```

#### `[formatting]`

| Setting                         | Required | Description                                                                                                                                                                      | Example |
| ------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| `source_currency_use_locale`    | Yes      | Controls locale-aware formatting for source-currency values (localized symbols, decimal/thousands separators, currency placement) when `true`; a consistent format when `false`. | `true`  |
| `exchanged_currency_use_locale` | Yes      | Same as above, applied to converted currency values.                                                                                                                             | `true`  |

#### `[general]`

| Setting             | Required | Description                                                                 | Example |
| ------------------- | -------- | --------------------------------------------------------------------------- | ------- |
| `reset_after_hours` | Yes      | Number of hours after which a reset becomes required. Minimum value is `6`. | `24`    |

---

## Portfolio Configuration

[`settings/portfolio.toml`](./settings/portfolio.toml) defines which Steam items are tracked.

```toml
["Fracture Case"]
link = "https://steamcommunity.com/market/listings/730/Fracture%20Case"
quantity = 50
purchase_price_per_item = "0.25"

["Dreams & Nightmares Case"]
link = "https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case"
quantity = 40
purchase_price_per_item = "0.50"

["Revolution Case"]
link = "https://steamcommunity.com/market/listings/730/Revolution%20Case"
quantity = 30
purchase_price_per_item = "0.25"

["Recoil Case"]
link = "https://steamcommunity.com/market/listings/730/Recoil%20Case"
quantity = 20
purchase_price_per_item = "0.25"

["Snakebite Case"]
link = "https://steamcommunity.com/market/listings/730/Snakebite%20Case"
quantity = 10
purchase_price_per_item = "0.25"
```

| Field                     | Description                        |
| ------------------------- | ---------------------------------- |
| Item name (table header)  | Name of the Steam Market item      |
| `link`                    | Steam Community Market listing URL |
| `quantity`                | Number of units owned              |
| `purchase_price_per_item` | Original purchase cost of one unit |

> **Note:** `purchase_price_per_item` is stored as a string in the TOML configuration (e.g. `"0.25"`), not a numeric value.

Minimal example for a single item:

```toml
["Example Item Name"]
link = "https://steamcommunity.com/market/listings/730/Example"
quantity = 10
purchase_price_per_item = "0.25"
```

---

## Usage

The main executable is:

```bash
cs2-storage-unit-tracker
```

### Quick Start

```text
1. Install the application.
2. Configure Steam API settings.
3. Configure the portfolio.
4. Run the CLI.
5. Monitor synchronization progress.
6. Review the generated report.
```

There are no additional CLI arguments or subcommands provided at this time.

---

## CLI in Action

While synchronization is running, the CLI shows item processing and success/failure status:

![CLI processing items](./images/cli-item.png)

Once synchronization finishes, the CLI displays progress, status messages, financial information, interactive confirmations where relevant, and the final aggregated report information:

![CLI report output](./images/cli-report.png)

---

## Reports

At the end of a synchronization run, the application generates a report in **.txt** format containing the aggregated financial information for the synchronized items.

- Reports are generated after a synchronization run completes.
- Reports may reflect either a successful or an unsuccessful synchronization result.
- If a run is interrupted after some items have already been processed, a **partial report** can still be generated.
- Reports are stored in the [`reports/`](./reports/) directory.

```text
reports/
├── .gitkeep
└── portfolio__YYYY-MM-D.txt
```

_Example filename shown — actual reports are generated with the real date, e.g. `portfolio__1970-01-01.txt`._

---

## API / External Services

### Steam Community Market

The application uses Steam Community Market data to obtain current item prices.

The Steam game App ID and the retrieval currency are configurable:

```toml
[steam_api]
app_id = 730
currency = "USD"
```

### Frankfurter

The application can optionally use [Frankfurter](https://frankfurter.dev/) for currency exchange rates.

Currency conversion is enabled by specifying a target currency:

```toml
[frankfurter_api]
to_currency = "EUR"
```

Conversion is disabled when the value is left empty:

```toml
to_currency = ""
```

---

## Rate Limits and Synchronization Behavior

The application:

- tracks the number of requests used
- calculates remaining requests before synchronization
- detects when no requests remain
- can perform a partial synchronization when there are not enough requests for every outdated item
- asks the user for confirmation before performing a partial run
- uses a configured delay between requests
- persists progress so synchronization state can be retained
- supports continuing after individual item request failures

---

## Error Handling and Limitations

### Error handling

The application handles the following scenarios:

- failed Steam price requests
- failed currency exchange-rate requests
- exhausted daily request allowance
- insufficient requests for a complete synchronization
- user cancellation
- repeated/recent execution
- keyboard interruption (`Ctrl+C`)
- failed individual items

An individual item failure does not necessarily stop the entire synchronization process. When interrupted with `Ctrl+C`, the application persists its current state and can emit a partial report when some items have already been processed.

### Limitations

- Steam App ID correctness is not validated at runtime.
- An incorrect Steam App ID may cause failed API requests.
- Currency conversion depends on the availability of the configured exchange-rate service.
- Synchronization is subject to the application's request limits.
- Not every item may be synchronized in a single run when the remaining request quota is insufficient.

---

## Project Structure

The core architecture is organized around a few responsibilities:

- **[`api/`](./src/cs2_storage_unit_tracker/api/)** — clients for external services (Steam, Frankfurter).
- **[`cli/`](./src/cs2_storage_unit_tracker/cli/)** — the CLI entry point, application wiring ([`app.py`](./src/cs2_storage_unit_tracker/cli/app.py), [`app_factory.py`](./src/cs2_storage_unit_tracker/cli/app_factory.py)), and terminal rendering ([`content/`](./src/cs2_storage_unit_tracker/cli/content/), [`renderers/`](./src/cs2_storage_unit_tracker/cli/renderers)).
- **[`config/`](./src/cs2_storage_unit_tracker/config/)** — configuration loading ([`loaders/`](./src/cs2_storage_unit_tracker/config/loaders/)) and data/state models ([`models/`](./src/cs2_storage_unit_tracker/config/models/)).
- **[`data/`](./src/cs2_storage_unit_tracker/data/)** — application runtime and synchronization state.
- **[`formatting/`](./src/cs2_storage_unit_tracker/formatting/)** — currency display formatting.
- **[`helpers/`](./src/cs2_storage_unit_tracker/helpers/)** — shared utilities (decimal handling, error types, Pydantic helpers, status data).

---

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0).

See the [`LICENSE`](./LICENSE) file for details.

---

## Author / Contact

- **Author:** Jakub Gawron
- **GitHub:** [github.com/JakubGawron](https://github.com/JakubGawron)
- **Repository:** [github.com/JakubGawron/cs2-storage-unit-tracker](https://github.com/JakubGawron/cs2-storage-unit-tracker)
- **Contact:** [contact.jakub.gawron@gmail.com](mailto:contact.jakub.gawron@gmail.com)
