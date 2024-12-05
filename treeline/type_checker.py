from dataclasses import dataclass
from typing import Any, Type, TypeVar, Union, get_args, get_origin, get_type_hints

T = TypeVar("T")


class ValidationError(Exception):
    pass


class TypeValidator:
    """A simple type validation system for runtime type checking."""

    @staticmethod
    def validate(value: Any, expected_type: Type[T]) -> None:
        """Validate that a value matches its expected type."""
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if origin is Union and type(None) in args:
            if value is None:
                return
            other_type = next(t for t in args if t is not type(None))
            expected_type = other_type

        if origin is list:
            if not isinstance(value, list):
                raise ValidationError(f"Expected list but got {type(value)}")
            element_type = args[0]
            for item in value:
                TypeValidator.validate(item, element_type)
            return

        if origin is dict:
            if not isinstance(value, dict):
                raise ValidationError(f"Expected dict but got {type(value)}")
            key_type, value_type = args
            for k, v in value.items():
                TypeValidator.validate(k, key_type)
                TypeValidator.validate(v, value_type)
            return

        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Expected type {expected_type.__name__} but got {type(value).__name__}"
            )


@dataclass
class ValidatedModel:
    """Base class for type-validated models."""

    def __post_init__(self):
        """Validate types after initialization."""
        hints = get_type_hints(self.__class__)

        for field_name, expected_type in hints.items():
            value = getattr(self, field_name)
            try:
                TypeValidator.validate(value, expected_type)
            except ValidationError as e:
                raise ValidationError(f"Field '{field_name}': {str(e)}")
