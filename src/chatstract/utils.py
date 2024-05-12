from typing import Optional, Type, Any, Tuple, List, get_origin, get_args, Union
from types import NoneType
from copy import deepcopy

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def partial_model(model: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a version of a Pydantic model where all fields are optional.
    Code from: https://stackoverflow.com/a/76560886
    """
    def make_field_optional(field: FieldInfo, default: Any = None) -> Tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation]  # type: ignore
        return new.annotation, new
    return create_model(
        f'Partial{model.__name__}',
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        }
    )

def list_mandatory(model: Type[BaseModel]) -> List[str]:
    """
    List the mandatory fields of a Pydantic model.
    """
    mandatory_fields = []
    for name, field in model.model_fields.items():
        # Check if the field is Optional
        field_type = field.annotation
        origin = get_origin(field_type)
        args = get_args(field_type)
        is_optional = origin is Union and any(arg is NoneType for arg in args)
        if not is_optional:
            mandatory_fields.append(name)

    return mandatory_fields