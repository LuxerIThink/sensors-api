from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from app.models import Measurement

MeasurementInPydantic = pydantic_model_creator(
    Measurement,
    name="MeasurementIn",
    exclude_readonly=True,
    exclude=("uuid", "sensor_id"),
)

MeasurementInPydanticAllOptional = pydantic_model_creator(
    Measurement,
    name="MeasurementInOptional",
    exclude_readonly=True,
    exclude=("uuid", "sensor_id"),
    optional=("time", "value"),
)

MeasurementOutPydantic = pydantic_model_creator(
    Measurement,
    name="MeasurementOut",
    exclude=("sensor", "sensor_id"),
)

MeasurementsOutPydantic = pydantic_queryset_creator(
    Measurement,
    name="MeasurementsOut",
    exclude=("sensor", "sensor_id"),
)
