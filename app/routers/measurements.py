from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction

from app.models import Measurement
from app.pydantics.measurement import (
    MeasurementsOutPydantic,
    MeasurementOutPydantic,
    MeasurementInPydanticAllOptional,
    MeasurementInPydantic,
)

router = APIRouter(
    prefix="/measurements",
    tags=["measurements"],
)


@router.get("/", response_model=MeasurementsOutPydantic)
async def get_measurement(
    user_id: Annotated[dict, Depends(authorize)],
    sensor_uuid: str = "",
    uuid: str = "",
    start_time: datetime | None = None,
    finish_time: datetime | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
):
    parameters = {
        "uuid": uuid,
        "sensor_id": sensor_uuid,
        "time__gte": start_time,
        "time__lte": finish_time,
        "value__gte": min_value,
        "value__lte": max_value,
    }
    filtered_parameters = {key: value for key, value in parameters.items() if value}
    async with in_transaction():
        measurements = await Measurement.filter(user_id=user_id, **filtered_parameters)
        if not measurements and uuid or sensor_uuid:
            measurements = await Measurement.filter(
                **filtered_parameters, sensor__device__is_shared=True
            )
        return measurements


@router.post("/{sensor_uuid}", response_model=MeasurementOutPydantic)
async def create_measurement(
    user_id: Annotated[dict, Depends(authorize)],
    sensor_uuid: str,
    measurement: MeasurementInPydantic,
):
    return await Measurement.create(
        **measurement.model_dump(), sensor_id=sensor_uuid, user_id=user_id
    )


@router.put("/{uuid}", response_model=MeasurementOutPydantic)
async def edit_measurement(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    measurement_in: MeasurementInPydantic,
):
    measurement_dict = measurement_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        measurement = await Measurement.get(uuid=uuid, user_id=user_id)
        await measurement.update_from_dict(measurement_dict).save(
            update_fields=measurement_dict.keys()
        )
        return measurement


@router.patch("/{uuid}", response_model=MeasurementOutPydantic)
async def edit_measurement(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    measurement_in: MeasurementInPydanticAllOptional,
):
    measurement_dict = measurement_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        measurement = await Measurement.get(uuid=uuid, user_id=user_id)
        await measurement.update_from_dict(measurement_dict).save(
            update_fields=measurement_dict.keys()
        )
        return measurement


@router.delete("/{uuid}", response_model=MeasurementOutPydantic)
async def remove_measurement(user_id: Annotated[dict, Depends(authorize)], uuid: str):
    async with in_transaction():
        measurement = await Measurement.get(uuid=uuid, user_id=user_id)
        await measurement.delete()
        return measurement
