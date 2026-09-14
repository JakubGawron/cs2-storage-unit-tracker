"""Centralized filesystem path management for application configuration and data.

This class provides a single source of truth for all configuration, settings,
and data file paths. It ensures consistent path resolution across the application
and supports both user-level settings and project-level runtime data.

Attributes:
    root_dir: Root directory for user-level configuration, settings, and
        reports (typically ~/.config/cs2_tracker or equivalent).
    project_dir: Project-level directory for application runtime data and
        internal state (typically ~/.local/share/cs2_tracker or equivalent).

The class is immutable (frozen=True) and uses slots for memory efficiency.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Paths:
    """Centralized filesystem path management for application configuration and data."""

    root_dir: Path
    project_dir: Path

    @property
    def reports(self) -> Path:
        """Directory path for timestamped text reports.

        Returns:
            Path to the reports directory where MarkdownDocument instances
                write timestamped report files.
        """
        return self.root_dir / "reports"

    @property
    def portfolio(self) -> Path:
        """File path for portfolio configuration.

        Returns:
            Path to the portfolio.toml file containing portfolio settings
                and tracked inventory configuration.
        """
        return self.root_dir / "settings" / "portfolio.toml"

    @property
    def runtime(self) -> Path:
        """File path for application runtime state.

        Returns:
            Path to the runtime.toml file containing transient application
                state and execution metadata.
        """
        return self.project_dir / "data" / "runtime.toml"

    @property
    def sync_status(self) -> Path:
        """File path for external data synchronization status.

        Returns:
            Path to the sync_status.toml file containing synchronization
                timestamps and status for Frankfurter and Steam APIs.
        """
        return self.project_dir / "data" / "sync_status.toml"

    @property
    def user_settings(self) -> Path:
        """File path for user preferences and API credentials.

        Returns:
            Path to the settings.toml file containing user preferences,
                API credentials, and formatting options.
        """
        return self.root_dir / "settings" / "settings.toml"
