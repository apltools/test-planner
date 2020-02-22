from django.db import models

# Create your models here.
from django.utils.crypto import get_random_string


def generate_api_key(length: int = 32) -> str:
    return get_random_string(length=length)


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class APIKey(SingletonModel):
    key = models.CharField(max_length=32, default=generate_api_key)