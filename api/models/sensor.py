from tortoise import fields
from .abstract import AbstractBaseModel


class Sensor(AbstractBaseModel):
    name = fields.CharField(max_length=32)
    device = fields.ForeignKeyField(
        "models.Device",
        related_name="sensors",
        on_delete=fields.CASCADE
    )
    unit = fields.CharField(max_length=32)
    measurements = fields.ReverseRelation["Measurement"]