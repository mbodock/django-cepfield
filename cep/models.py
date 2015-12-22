from __future__ import unicode_literals
# encoding: utf-8

from django.db import models


class Cep(models.Model):
    codigo = models.CharField(max_length=8, unique=True)
    valido = models.BooleanField(default=False)
