"""Utilities for extracting and validating Pydantic validation context.

This module provides helper functions for safely accessing and validating
the context dictionary passed to Pydantic validators during model
instantiation or field validation.
"""

from typing import Any, cast

from pydantic import ValidationInfo


def get_validated_context(info: ValidationInfo) -> dict[str, Any]:
    """Extract and validate the context from a Pydantic ValidationInfo object.

    Retrieves the validation context from a ValidationInfo object, ensuring
    it exists and is a dictionary. This is typically used within Pydantic
    field validators or model validators to safely access contextual data
    passed during model instantiation.

    Args:
        info: A Pydantic ValidationInfo object provided to a validator.

    Returns:
        The validation context as a dictionary mapping string keys to values
        of any type.

    Raises:
        ValueError: If the context is None, not a dictionary, or missing
            from the ValidationInfo object.

    Examples:
        >>> from pydantic import BaseModel, field_validator, ValidationInfo
        >>> class MyModel(BaseModel):
        ...     value: int
        ...     @field_validator("value")
        ...     @classmethod
        ...     def validate_value(cls, v, info: ValidationInfo):
        ...         context = get_validated_context(info)
        ...         max_value = context.get("max_value", 100)
        ...         if v > max_value:
        ...             raise ValueError(f"Value must not exceed {max_value}")
        ...         return v
        >>> model = MyModel(value=50, context={"max_value": 75})
    """
    context: Any | None = info.context
    if context is None or not isinstance(context, dict):
        raise ValueError("Missing validation context")
    return cast(dict[str, Any], context)
