from tortoise import fields
from .abstract import AbstractBaseModel


class User(AbstractBaseModel):
    username = fields.CharField(max_length=32, unique=True)
    password = fields.CharField(max_length=128)
    email = fields.CharField(max_length=128, unique=True)