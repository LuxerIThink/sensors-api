from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction
from app.models import Sensor
from app.pydantics.sensor import (
    SensorOutPydantic,
    SensorInPydantic,
    SensorsOutPydantic,
    SensorInPydanticAllOptional,
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
    parameters = {
        "uuid__contains": uuid,
        "device_id__contains": device_uuid,
        "user_id": user_id,
        "name__contains": name,
        "unit__contains": unit,
    }
    return await Sensor.filter(**parameters)


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
    sensor_in: SensorInPydanticAllOptional,
):
    async with in_transaction():
        sensor = await Sensor.get(uuid=uuid, user_id=user_id)
        sensor_dict = sensor_in.model_dump(exclude_none=True, exclude_unset=True)
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
