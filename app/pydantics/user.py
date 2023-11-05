from tortoise.contrib.pydantic import pydantic_model_creator

from app.internal.pydantics import all_optional
from app.models import User

UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
)


UserInPydanticAllOptional = all_optional(UserInPydantic)


UserOutPydantic = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password", "devices")
)


