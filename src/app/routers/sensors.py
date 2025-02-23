from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction
from app.models import Sensor
from app.pydantics.sensor import (
    SensorOutPydantic,
    SensorInPydantic,
    SensorsOutPydantic,
    SensorInOptionalPydantic,
)

router = APIRouter(
    prefix="/sensors",
    tags=["sensors"],
)


@router.get("/", response_model=SensorsOutPydantic)
async def get_sensor(
    user_id: Annotated[dict, Depends(authorize)],
    device_uuid: str = "",
    uuid: str = "",
    name: str = "",
    unit: str = "",
):
    params_template = {
        "uuid": uuid,
        "device_id": device_uuid,
        "name__contains": name,
        "unit__contains": unit,
    }
    params = {key: value for key, value in params_template.items() if value}
    async with in_transaction():
        sensors = await Sensor.filter(user_id=user_id, **params)
        if not sensors and (uuid or device_uuid):
            sensors = await Sensor.filter(**params, device__is_shared=True)
        return sensors


@router.post("/{device_uuid}", response_model=SensorOutPydantic)
async def create_sensor(
    user_id: Annotated[dict, Depends(authorize)],
    device_uuid: str,
    sensor: SensorInPydantic,
):
    return await Sensor.create(
        **sensor.model_dump(), device_id=device_uuid, user_id=user_id
    )


@router.put("/{uuid}", response_model=SensorOutPydantic)
async def edit_sensor(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    sensor_in: SensorInPydantic,
):
    sensor_dict = sensor_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        sensor = await Sensor.get(uuid=uuid, user_id=user_id)
        await sensor.update_from_dict(sensor_dict).save(
            update_fields=sensor_dict.keys()
        )
        return sensor


@router.patch("/{uuid}", response_model=SensorOutPydantic)
async def edit_partially_sensor(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    sensor_in: SensorInOptionalPydantic,
):
    sensor_dict = sensor_in.model_dump(exclude_none=True, exclude_unset=True)
    async with in_transaction():
        sensor = await Sensor.get(uuid=uuid, user_id=user_id)
        await sensor.update_from_dict(sensor_dict).save(
            update_fields=sensor_dict.keys()
        )
        return sensor


@router.delete("/{uuid}", response_model=SensorOutPydantic)
async def remove_sensor(user_id: Annotated[dict, Depends(authorize)], uuid: str):
    async with in_transaction():
        sensor = await Sensor.get(uuid=uuid, user_id=user_id)
        await sensor.delete()
        return sensor
