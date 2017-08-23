from django.db import models
from django.contrib.postgres.fields import JSONField


class Log(models.Model):
    url = models.CharField(max_length=512)
    session = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    user = models.CharField(max_length=256)
    additional = JSONField()
