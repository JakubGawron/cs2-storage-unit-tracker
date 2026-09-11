import re
from typing import Any, LiteralString

from cs2_storage_unit_tracker.cli.content.rich import components
from cs2_storage_unit_tracker.cli.renderers.flatten import flatten_and_format

STATUS_HEADERS: set[components.Style] = {
    components.Style.FAILED_HEADER,
    components.Style.SUCCESSFUL_HEADER,
}


class TextRenderer:
    HEADER_WIDTH: components.LayoutWidth = components.LayoutWidth.HEADER

    def render(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> str:
        parts: list[tuple[str, components.Style | None]] = flatten_and_format(
            content=components.COMPONENTS[key].content,
            variables=variables,
        )

        lines: list[list[tuple[str, components.Style | None]]] = self._flatten_lines(
            parts
        )

        output: list[str] = []
        for line in lines:
            if not line:
                continue

            output.append(self._render_line(line))

        return "".join(output)

    @staticmethod
    def _flatten_lines(
        parts: list[tuple[str, components.Style | None]],
    ) -> list[list[tuple[str, components.Style | None]]]:
        lines: list[list[tuple[str, components.Style | None]]] = []
        current: list[tuple[str, components.Style | None]] = []

        for text, style in parts:
            if not text:
                continue

            for chunk in text.splitlines(keepends=True):
                value: str = chunk.rstrip("\r\n")
                has_newline: bool = chunk.endswith(("\n", "\r"))

                if value:
                    current.append((value, style))

                if has_newline:
                    lines.append(current)
                    current = []

        if current:
            lines.append(current)

        return lines

    def _render_line(
        self,
        parts: list[tuple[str, components.Style | None]],
    ) -> str:
        styles: set[components.Style | None] = {style for _, style in parts}
        text: str = "".join(value for value, _ in parts).strip()

        if not text:
            return "\n"

        if styles & STATUS_HEADERS:
            return self._render_status(text)

        if components.Style.REPORT_HEADER in styles:
            return self._render_main_header(text)

        if components.Style.ITEM_HEADER in styles:
            return self._render_item_header(text)

        return f"{text}\n"

    def _render_main_header(self, text: str) -> str:

        line: LiteralString = "=" * self.HEADER_WIDTH

        return f"{line}\n{text}\n{line}\n"

    def _render_item_header(self, text: str) -> str:

        line: LiteralString = "-" * self.HEADER_WIDTH

        return f"\n\n{line}\n{text}\n{line}\n"

    def _render_status(self, text: str) -> str:
        text = re.sub(
            r"\((\d+/\d+)\)",
            r"[\1]",
            text,
        )

        return f"{'-' * self.HEADER_WIDTH}\n{text}\n{'-' * self.HEADER_WIDTH}"
