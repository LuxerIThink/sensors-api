from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import Sensor

SensorInPydantic = pydantic_model_creator(
    Sensor,
    name="SensorIn",
    exclude_readonly=True,
)
SensorOutPydantic = pydantic_model_creator(
    Sensor,
    name="SensorOut"
)
