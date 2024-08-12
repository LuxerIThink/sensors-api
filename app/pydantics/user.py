from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from app.models import User

UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
)


UserInPydanticAllOptional = pydantic_model_creator(
    User,
    name="UserInEdit",
    exclude_readonly=True,
    optional=("username", "password", "email"),
)


UserOutPydantic = pydantic_model_creator(
    User, name="UserOut", exclude=("password", "devices", "sensors", "measurements")
)

UsersOutPydantic = pydantic_queryset_creator(
    User, name="UserOut", exclude=("password", "devices", "sensors", "measurements")
)
