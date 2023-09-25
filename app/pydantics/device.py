from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import Device

DeviceInPydantic = pydantic_model_creator(
    Device,
    name="DeviceIn",
    exclude_readonly=True,
)
UserOutPydantic = pydantic_model_creator(
    Device,
    name="DeviceOut"
)
