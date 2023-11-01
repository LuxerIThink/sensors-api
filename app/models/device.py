from tortoise import fields
from .abstract import AbstractBaseModel
from .user import User


class Device(AbstractBaseModel):
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.User", "devices", fields.CASCADE
    )
    name = fields.CharField(min_length=2, max_length=32)
    is_shared = fields.BooleanField(default=False)
    sensors = fields.ReverseRelation["Sensor"]

    class Meta:
        unique_together = (("name", "user"),)
