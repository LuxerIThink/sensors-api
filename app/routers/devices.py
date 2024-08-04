from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction
from app.models import Device
from app.pydantics.device import (
    DeviceOutPydantic,
    DeviceInPydantic,
    DevicesOutPydantic,
    DeviceInPydanticAllOptional,
)

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.get("/", response_model=DevicesOutPydantic)
async def get_device(user_id: Annotated[dict, Depends(authorize)], uuid: str = ""):
    devices = await Device.filter(uuid__contains=uuid, user_id=user_id)
    return devices


@router.post("/", response_model=DeviceOutPydantic)
async def create_device(
    user_id: Annotated[dict, Depends(authorize)], device: DeviceInPydantic
):
    return await Device.create(**device.model_dump(), user_id=user_id)


@router.put("/{uuid}", response_model=DeviceOutPydantic)
async def edit_device(
    user_id: Annotated[dict, Depends(authorize)],
    uuid: str,
    device_in: DeviceInPydanticAllOptional,
):
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        device_dict = device_in.model_dump(exclude_none=True, exclude_unset=True)
        await device.update_from_dict(device_dict).save(
            update_fields=device_dict.keys()
        )
    return device


@router.delete("/{uuid}", response_model=DeviceOutPydantic)
async def remove_device(user_id: Annotated[dict, Depends(authorize)], uuid: str):
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        await device.delete()
    return device
