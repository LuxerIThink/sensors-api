from pydantic import create_model


def all_optional(Pydantic):
    annotations = {}
    for base in Pydantic.__mro__:
        if hasattr(base, '__annotations__'):
            annotations.update(base.__annotations__)

    for field_name, field_info in Pydantic.__annotations__.items():
        if not field_name.startswith('__'):
            field_type = annotations[field_name]
            if not hasattr(field_type, "__args__") or len(field_type.__args__) == 1:
                annotations[field_name] = (field_type, None)

    return create_model(Pydantic.__name__ + 'AllOptional', **annotations)
