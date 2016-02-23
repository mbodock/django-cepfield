# encoding: utf-8
import requests

from django import forms
from django.core.exceptions import ValidationError

from .models import Cep
from .parser import Parser


class CepField(forms.RegexField):
    SERVICE_URL = 'http://m.correios.com.br/movel/buscaCepConfirma.do'

    def __init__(self, should_raise_exception=True, *args, **kwargs):
        super(CepField, self).__init__(r'^\d{2}\.?\d{3}-?\d{3}',
                                       *args,
                                       **kwargs)
        self.should_raise_exception = should_raise_exception
        self.dados = {
            'bairro': None,
            'logradouro': None,
            'estado': None,
            'cidade': None,
            'cliente': None,
        }
        self.valido = False

    def clean(self, value):
        original_value = value
        value = super(CepField, self).clean(value)
        value = value.strip('.: ')
        cep = Cep.objects.get_or_create(codigo=value)
        if cep.valido:
            return cep

        if not self.valida_correios(value):
            raise ValidationError(u'Invalid CEP')

        cep.valido = self.valido
        if cep.valido:
            cep.logradouro = self.dados.get('logradouro', self.dados.get('cliente', ''))
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
                {'metodo': 'buscarCep', 'cepEntrada': codigo})
            parse = Parser(response.content)
            self.dados = parse.get_data()
        except requests.RequestException:
            if self.should_raise_exception:
                raise ValidationError('Cannot validade with Correios')
            return True

        if 'Dados nao encontrados' in response.content:
            return False
        self.valido = True
        return True
