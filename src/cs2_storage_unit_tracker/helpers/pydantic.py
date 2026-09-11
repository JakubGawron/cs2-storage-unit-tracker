from typing import Any, cast

from pydantic import ValidationInfo


def get_validated_context(info: ValidationInfo) -> dict[str, Any]:
    context: Any | None = info.context
    if context is None or not isinstance(context, dict):
        raise ValueError("Missing validation context")
    return cast(dict[str, Any], context)
