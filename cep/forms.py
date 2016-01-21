# encoding: utf-8
import requests

from django import forms
from django.core.exceptions import ValidationError

from .models import Cep


class CepField(forms.RegexField):
    WEB_SERVICE_URL = 'http://m.correios.com.br/movel/buscaCepConfirma.do'

    def __init__(self, raise_exception=True, *args, **kwargs):
        super(CepField, self).__init__(r'^\d{2}\.?\d{3}-?\d{3}', strip=True, *args, **kwargs)
        self.raise_exception = raise_exception

    def clean(self, value):
        original_value = value
        value = super(CepField, self).clean(value)
        value = value.replace('-', '').replace('.', '')
        cep = Cep.objects.get_or_create(codigo=value)
        if cep.valido:
            return original_value

        if not self.valida_correios(value):
            raise ValidationError(u'Invalid CEP')

        cep.valido = True
        cep.save()
        return original_value

    def valida_correios(self, codigo):
        try:
            result = requests.post(
                self.WEB_SERVICE_URL,
                {'metodo': 'buscarCep', 'cepEntrada': codigo})
        except:
            if self.raise_exception:
                raise ValidationError('Cannot validade with Correios')
            return True

        if 'Dados nao encontrados' in result.content:
            return False
        self.valido = True
        return True
