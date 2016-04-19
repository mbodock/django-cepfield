# encoding: utf-8
from __future__ import unicode_literals
import requests

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Cep
from .parser import Parser


class CepField(forms.RegexField):
    SERVICE_URL = 'http://m.correios.com.br/movel/buscaCepConfirma.do'
    invalid_cep = _('Invalid CEP')
    cannot_validate = _('Cannot validate with Correios')

    def __init__(self, force_correios_validation=True,
                 timeout=10, *args, **kwargs):
        super(CepField, self).__init__(r'^\d{2}\.?\d{3}-?\d{3}$',
                                       *args,
                                       **kwargs)
        self.force_correios_validation = force_correios_validation
        self.dados = {
            'bairro': None,
            'logradouro': None,
            'estado': None,
            'cidade': None,
            'cliente': None,
        }
        self.valido = False
        self.timeout = timeout

    def clean(self, value):
        original_value = value
        value = super(CepField, self).clean(value)
        value = value.replace('.', '').replace('-', '').strip(' :')
        cep = Cep.objects.get_or_create(codigo=value)
        cep.original_value = original_value
        if cep.valido:
            return cep

        if not self.valida_correios(value):
            raise ValidationError(self.invalid_cep)

        cep.valido = self.valido
        if cep.valido:
            cep.logradouro = self.dados.get('logradouro',
                                            self.dados.get('cliente', ''))
            cep.bairro = self.dados.get('bairro', '')
            cep.estado = self.dados.get('estado', '')
            cep.cidade = self.dados.get('cidade', '')
            cep.complemento = self.dados.get('complemento', '')
        cep.save()
        return cep

    def valida_correios(self, codigo):
        try:
            response = requests.post(
                self.SERVICE_URL,
                {'metodo': 'buscarCep', 'cepEntrada': codigo},
                timeout=self.timeout)
            parser = Parser(response.content)
            self.dados = parser.get_data()
        except requests.RequestException:
            if self.force_correios_validation:
                raise ValidationError(self.cannot_validate)
            return True

        if 'Dados nao encontrados' in parser.content:
            return False
        self.valido = True
        return True
