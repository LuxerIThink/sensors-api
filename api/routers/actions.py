from fastapi import APIRouter

router = APIRouter(
    prefix="/actions",
    tags=["actions"],
)


@router.get("/token")
async def get_token():
    return {"message": "Hello World"}