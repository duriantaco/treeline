from dataclasses import dataclass
from typing import Any, Type, Union, get_args, get_origin


class TypeValidator:
    @staticmethod
    def validate(value: Any, expected_type: Type) -> None:
        """
        Validates that a value matches the expected type, with support for generics.

        Args:
            value: The value to validate
            expected_type: The expected type (can be a generic type)

        Raises:
            TypeError: If the value doesn't match the expected type
        """
        origin = get_origin(expected_type)
        if origin is Union:
            args = get_args(expected_type)
            if len(args) == 2 and args[1] is type(None):
                if value is None:
                    return
                expected_type = args[0]
                origin = get_origin(expected_type)

        if value is None:
            if expected_type is type(None):
                return
            raise TypeError(f"Expected {expected_type}, got None")

        if origin is not None:
            args = get_args(expected_type)

            if origin == list:
                if not isinstance(value, list):
                    raise TypeError(f"Expected list, got {type(value)}")
                for item in value:
                    TypeValidator.validate(item, args[0])

            elif origin == dict:
                if not isinstance(value, dict):
                    raise TypeError(f"Expected dict, got {type(value)}")
                key_type, value_type = args
                for k, v in value.items():
                    TypeValidator.validate(k, key_type)
                    TypeValidator.validate(v, value_type)

            elif origin == tuple:
                if not isinstance(value, tuple):
                    raise TypeError(f"Expected tuple, got {type(value)}")
                if len(value) != len(args):
                    raise TypeError(
                        f"Expected tuple of length {len(args)}, got length {len(value)}"
                    )
                for item, item_type in zip(value, args):
                    TypeValidator.validate(item, item_type)

            elif origin == set:
                if not isinstance(value, set):
                    raise TypeError(f"Expected set, got {type(value)}")
                for item in value:
                    TypeValidator.validate(item, args[0])
        else:
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(value)}")


@dataclass
class TypeChecked:
    """Base class for type-checked dataclasses"""

    def __post_init__(self):
        """Validate types after initialization"""
        for field_name, field_type in self.__annotations__.items():
            value = getattr(self, field_name)
            try:
                TypeValidator.validate(value, field_type)
            except TypeError as e:
                raise TypeError(f"Invalid type for {field_name}: {str(e)}")


class ValidationError(Exception):
    """Raised when type validation fails"""

    pass
