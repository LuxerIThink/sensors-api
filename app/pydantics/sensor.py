from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from app.models import Sensor

SensorInPydantic = pydantic_model_creator(
    Sensor, name="SensorIn", exclude_readonly=True, exclude=("uuid", "device_id", "user", "user_id")
)

SensorInPydanticAllOptional = pydantic_model_creator(
    Sensor,
    name="SensorsInOptional",
    exclude_readonly=True,
    exclude=("uuid", "device_id", "user", "user_id"),
    optional=("name", "unit"),
)

SensorOutPydantic = pydantic_model_creator(
    Sensor,
    name="SensorOut",
    exclude=("measurements", "device", "device_id", "user", "user_id"),
)

SensorsOutPydantic = pydantic_queryset_creator(
    Sensor,
    name="SensorsOut",
    exclude=("measurements", "device", "device_id", "user", "user_id"),
)
