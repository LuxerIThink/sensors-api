from tortoise import fields
from .abstract import AbstractBaseModel
from tortoise.contrib.pydantic import pydantic_model_creator


class User(AbstractBaseModel):
    username = fields.CharField(max_length=32, unique=True)
    password = fields.TextField(max_length=128)
    email = fields.CharField(max_length=32, unique=True)
    devices = fields.ReverseRelation["Device"]


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
