from tortoise.contrib.pydantic import pydantic_model_creator
from app.models import User

UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
)
UserOutPydantic = pydantic_model_creator(
    User,
    name="UserOut",
    exclude=("password",)
)
