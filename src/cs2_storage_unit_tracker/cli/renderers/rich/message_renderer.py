from dataclasses import dataclass
from typing import Any

from cs2_storage_unit_tracker.cli.content.rich import messages
from cs2_storage_unit_tracker.cli.renderers.rich.console_instance import console
from rich.prompt import Confirm
from rich.text import Text


@dataclass(frozen=True, slots=True)
class RichMessageRenderer:
    @staticmethod
    def _check_type(received_type: messages.Type, expected_type: messages.Type) -> None:
        if received_type is not expected_type:
            raise ValueError(
                f"Invalid type: {received_type!r}. Expected: {expected_type!r}"
            )

    def _get_template_typecheck(
        self, key: messages.Key, expected_type: messages.Type
    ) -> messages.Template:
        try:
            template: messages.Template = messages.MESSAGES[key]
            self._check_type(received_type=template.type, expected_type=expected_type)
            return template
        except KeyError as exc:
            raise ValueError(
                f"No message template exists for key {key.value!r}"
            ) from exc

    @staticmethod
    def _format_text_parts(
        segments: tuple[messages.Segment, ...], variables: dict[str, Any] | None = None
    ) -> list[tuple[str, str]]:
        if variables is None:
            parts: list[tuple[str, str]] = [
                (segment.text, segment.style.value) for segment in segments
            ]
        else:
            parts: list[tuple[str, str]] = [
                (
                    segment.text.format_map(variables),
                    segment.style.value,
                )
                for segment in segments
            ]
        return parts

    def print(self, key: messages.Key, variables: dict[str, Any] | None = None) -> None:
        template: messages.Template = self._get_template_typecheck(
            key=key, expected_type=messages.Type.PRINT
        )

        parts: list[tuple[str, str]] = [
            (template.icon, ""),
            *self._format_text_parts(segments=template.segments, variables=variables),
        ]

        console.print(Text.assemble(*parts))

    def confirm(
        self,
        key: messages.Key,
        default: bool = False,
        variables: dict[str, Any] | None = None,
    ) -> bool:
        template: messages.Template = self._get_template_typecheck(
            key=key, expected_type=messages.Type.CONFIRM
        )

        parts: list[tuple[str, str]] = [
            (template.icon, ""),
            *self._format_text_parts(segments=template.segments, variables=variables),
        ]

        result: bool = Confirm.ask(
            Text.assemble(*parts), default=default, console=console
        )

        return result

    @staticmethod
    def clear() -> None:
        console.clear()
