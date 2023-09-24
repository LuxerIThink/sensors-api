from tortoise import fields
from .abstract import AbstractBaseModel
from .sensor import Sensor


class Measurement(AbstractBaseModel):
    sensor: fields.ForeignKeyRelation[Sensor] = fields.ForeignKeyField(
        "app.Sensor", "measurements", fields.CASCADE
    )
    time = fields.DatetimeField()
    value = fields.FloatField()
