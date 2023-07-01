from tortoise import fields
from .abstract import AbstractBaseModel
from .device import Device


class Sensor(AbstractBaseModel):
    name = fields.CharField(min_length=2, max_length=32)
    device: fields.ForeignKeyRelation[Device] = fields.ForeignKeyField(
        "api.Device",
        "sensors",
        fields.CASCADE)
    unit = fields.CharField(max_length=32, null=True)
    measurements = fields.ReverseRelation["Measurement"]

    class Meta:
        unique_together = (("name", "device"),)
