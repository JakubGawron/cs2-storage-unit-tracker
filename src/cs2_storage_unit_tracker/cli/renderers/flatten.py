"""Utilities for flattening and formatting component structures into styled text.

This module provides functions to recursively resolve component templates,
apply variable substitution, and calculate padding to produce styled text
tuples suitable for rendering with the rich library.
"""

from typing import Any

from cs2_storage_unit_tracker.cli.content.rich import components


def flatten_and_format(
    content: tuple[components.Segment | components.Group | components.Key, ...],
    variables: dict[str, Any] | None = None,
) -> list[tuple[str, components.Style | None]]:
    """Recursively flatten and format component content into styled text tuples.

    Resolves nested templates referenced by Key objects, applies variable
    substitution using `str.format_map()`, and calculates padding based on
    min_width constraints for both Segment and Group objects.

    Args:
        content: Tuple of component items (Segment, Group, or Key objects)
            to flatten and format. Key objects are recursively resolved to
            their template content via COMPONENTS registry.
        variables: Optional dictionary of variables for substitution in
            Segment and Group text via `str.format_map()`. If None, no
            substitution is performed.

    Returns:
        List of (text, style) tuples representing styled text ready for
        rich library rendering. Each tuple contains plain text and an
        optional Style enum value.

    Raises:
        KeyError: If a Key reference is not found in the COMPONENTS registry.
        KeyError: If variable substitution fails due to missing keys in the
            variables dictionary.
        ValueError: If variable substitution fails due to invalid format string
            syntax in Segment or Group text.

    Note:
        Padding is applied as follows:
        - For Segment: Text is padded to segment.min_width with spaces.
        - For Group: After all segments are collected, if group.min_width
          exceeds current width, trailing whitespace is appended to reach
          the target width.
    """
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
