from typing import Annotated
from fastapi import APIRouter, Depends
from app.internal.authentication import authorize
from tortoise.transactions import in_transaction
from app.models import Device
from app.pydantics.device import DeviceOutPydantic, DeviceInPydantic, DevicesOutPydantic

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.get("/{uuid}", response_model=DevicesOutPydantic)
async def get_device(uuid: str, user_id: Annotated[dict, Depends(authorize)],):
    devices = await Device.filter(uuid=uuid, user_id=user_id)
    return devices


@router.post("/", response_model=DeviceOutPydantic)
async def create_device(user_id: Annotated[dict, Depends(authorize)], device: DeviceInPydantic):
    return await Device.create(**device.model_dump(), user_id=user_id)


@router.put("/{uuid}", response_model=DeviceOutPydantic)
async def edit_device(uuid: str, user_id: Annotated[dict, Depends(authorize)], device: DeviceInPydantic):
    async with in_transaction():
        await Device.filter(user_id=user_id, uuid=uuid).update(**device.model_dump(), user_id=user_id)
        device_new = await Device.get(uuid=uuid, user_id=user_id)
    return device_new


@router.delete("/{uuid}")
async def remove_device(uuid: str, user_id: Annotated[dict, Depends(authorize)]):
    async with in_transaction():
        device = await Device.get(uuid=uuid, user_id=user_id)
        await Device.filter(uuid=uuid, user_id=user_id).delete()
    return device
