from typing import Any

from cs2_storage_unit_tracker.cli.content.rich import components


def flatten_and_format(
    content: tuple[components.Segment | components.Group | components.Key, ...],
    variables: dict[str, Any] | None = None,
) -> list[tuple[str, components.Style | None]]:
    result: list[tuple[str, components.Style | None]] = []
    has_variables: bool = variables is not None

    for item in content:
        if isinstance(item, components.Key):
            template: components.Template = components.COMPONENTS[item]

            result.extend(
                flatten_and_format(
                    content=template.content,
                    variables=variables,
                )
            )

        elif isinstance(item, components.Group):
            group_parts: list[tuple[str, components.Style | None]] = []

            for segment in item.segments:
                text = (
                    segment.text.format_map(variables)
                    if has_variables
                    else segment.text
                )

                if segment.min_width is not None:
                    text = text.ljust(segment.min_width)

                group_parts.append((text, segment.style))

            if item.min_width is not None:
                current_width: int = sum(len(text) for text, _ in group_parts)
                padding: int = max(
                    0,
                    item.min_width - current_width,
                )

                result.extend(group_parts)

                if padding:
                    result.append((" " * padding, None))
            else:
                result.extend(group_parts)

        else:
            text: str = item.text.format_map(variables) if has_variables else item.text

            if item.min_width is not None:
                text = text.ljust(item.min_width)

            result.append((text, item.style))

    return result
