from __future__ import unicode_literals
# encoding: utf-8

from django.db import models


class CepManager(models.Manager):
    def get_or_create(self, codigo):
        try:
            return Cep.objects.get(codigo=codigo)
        except Cep.DoesNotExist:
            return Cep(codigo=codigo)


class Cep(models.Model):
    codigo = models.CharField(max_length=8, unique=True)
    valido = models.BooleanField(default=False)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=2)
    logradouro = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255)

    objects = CepManager()
