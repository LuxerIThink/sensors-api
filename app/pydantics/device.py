from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from app.models import Device

DeviceInPydantic = pydantic_model_creator(
    Device,
    name="DeviceIn",
    exclude_readonly=True,
    exclude=("uuid", "user_id"),
)

DeviceInPydanticAllOptional = pydantic_model_creator(
    Device,
    name="DeviceInOptional",
    exclude_readonly=True,
    exclude=("uuid", "user_id"),
    optional=("name", "is_shared")
)

DeviceOutPydantic = pydantic_model_creator(
    Device,
    name="DeviceOut",
    exclude=("sensors", "user", "user_id"),
)

DevicesOutPydantic = pydantic_queryset_creator(
    Device,
    exclude=("sensors", "user", "user_id"),
)


