from tortoise.contrib.pydantic import pydantic_model_creator

from app.internal.pydantics import AllOptional
from app.models import User

UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
)


class UserInPydanticAllOptional(UserInPydantic, metaclass=AllOptional):
    pass


UserOutPydantic = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password", "devices")
)


