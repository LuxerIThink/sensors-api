from tortoise import fields
from tortoise.models import Model


class AbstractBaseModel(Model):
    uuid = fields.UUIDField(primary_key=True)

    class Meta:
        abstract = True
