from tortoise import fields
from .abstract import AbstractBaseModel


class User(AbstractBaseModel):
    username = fields.CharField(min_length=3, max_length=32, unique=True)
    password = fields.CharField(min_length=8, max_length=128)
    email = fields.CharField(max_length=128, unique=True)
    devices = fields.ReverseRelation["Device"]