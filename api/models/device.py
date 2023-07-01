from tortoise import fields
from .abstract import AbstractBaseModel


class Device(AbstractBaseModel):
    name = fields.CharField(max_length=32, unique=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="devices",
        on_delete=fields.CASCADE
    )
    is_read_public = fields.BooleanField(default=False)
    sensors = fields.ReverseRelation["Sensor"]
