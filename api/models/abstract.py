from tortoise import fields
from tortoise.models import Model


class AbstractBaseModel(Model):
    uuid = fields.UUIDField(pk=True)

    class Meta:
        abstract = True
