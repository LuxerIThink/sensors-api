from tortoise import fields
from .user import User
from .abstract import AbstractBaseModel
from .sensor import Sensor


class Measurement(AbstractBaseModel):
    time = fields.DatetimeField()
    value = fields.FloatField()
    sensor: fields.ForeignKeyRelation[Sensor] = fields.ForeignKeyField(
        "app.Sensor", "measurements", fields.CASCADE
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.User", "measurements", fields.CASCADE
    )

    class Meta:
        unique_together = (("time", "sensor"),)
