from argon2 import PasswordHasher
from tortoise import fields
from app.internal.validators import PasswordValidator, EmailValidator
from .abstract import AbstractBaseModel
from tortoise.validators import MinLengthValidator


class User(AbstractBaseModel):
    username = fields.CharField(
        max_length=32, unique=True, validators=[MinLengthValidator(3)]
    )
    password = fields.CharField(max_length=128, validators=[PasswordValidator()])
    email = fields.CharField(max_length=32, unique=True, validators=[EmailValidator()])
    devices = fields.ReverseRelation["Device"]

    async def save(self, *args, **kwargs):
        password_hasher = PasswordHasher()
        self.password = password_hasher.hash(self.password)
        self.email = self.email.lower()
        await super().save(*args, **kwargs)
