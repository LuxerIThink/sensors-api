from tortoise import fields
from .abstract import AbstractBaseModel
from .user import User


class Device(AbstractBaseModel):
    name = fields.CharField(min_length=2, max_length=32)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "api.User", "devices", fields.CASCADE
    )
    is_read_public = fields.BooleanField(default=False)
    sensors = fields.ReverseRelation["Sensor"]

    class Meta:
        unique_together = (("name", "user"),)
