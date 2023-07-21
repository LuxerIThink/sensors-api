from tortoise import fields
from api.internal.validators import PasswordValidator, EmailValidator
from .abstract import AbstractBaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import MinLengthValidator
from ..startup.security import password_hasher


class User(AbstractBaseModel):
    username = fields.CharField(
        max_length=32, unique=True, validators=[MinLengthValidator(3)]
    )
    password = fields.CharField(max_length=128, validators=[PasswordValidator()])
    email = fields.CharField(max_length=32, unique=True, validators=[EmailValidator()])
    devices = fields.ReverseRelation["Device"]

    async def save(self, *args, **kwargs):
        self.password = password_hasher.hash(self.password)
        self.email = self.email.lower()
        await super().save(*args, **kwargs)


UserInPydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude_readonly=True,
)
UserOutPydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))
