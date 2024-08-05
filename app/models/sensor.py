from tortoise import fields
from .user import User
from .abstract import AbstractBaseModel
from .device import Device


class Sensor(AbstractBaseModel):
    name = fields.CharField(min_length=2, max_length=32)
    unit = fields.CharField(max_length=32, null=True)
    measurements = fields.ReverseRelation["Measurement"]
    device: fields.ForeignKeyRelation[Device] = fields.ForeignKeyField(
        "app.Device", "sensors", fields.CASCADE
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.User", "sensors", fields.CASCADE
    )

    class Meta:
        unique_together = (("name", "device"),)
