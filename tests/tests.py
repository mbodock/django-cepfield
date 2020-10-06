# encoding: utf-8
from __future__ import unicode_literals

import codecs
import os
import mock
import sys
import requests

test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_dir, os.path.pardir))
os.environ["DJANGO_SETTINGS_MODULE"] = 'tests.settings'

import django
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.exceptions import ValidationError
django.setup()
call_command('migrate', '--run-syncdb')

from cep.models import Cep
from cep.forms import CepField
from cep.parser import Engine, Parser, ParserEngine


class FakeRequest(object):
    def __init__(self, content):
        self.content = content


class FakeException(requests.RequestException):
    pass


def fake_request_success_brasilia(*args, **kwargs):
    with codecs.open('tests/responses/success.html', 'r', 'iso-8859-1') as f:
        return FakeRequest(f.read().encode('iso-8859-1'))


def fake_request_cep_desmembrado(*args, **kwargs):
    with codecs.open('tests/responses/cep-desmembrado.html', 'r', 'iso-8859-1') as f:
        return FakeRequest(f.read().encode('iso-8859-1'))


def fake_request_success_logradouro(*args, **kwargs):
    with codecs.open('tests/responses/success-logradouro.html',
                     'r',
                     'iso-8859-1') as f:
        return FakeRequest(f.read().encode('iso-8859-1'))


def fake_request_fail(*args, **kwargs):
    with codecs.open('tests/responses/error.html', 'r', 'iso-8859-1') as f:
        return FakeRequest(f.read().encode('iso-8859-1'))


def fake_request_fail_parser_quebrado(*args, **kwargs):
    with codecs.open('tests/responses/error-quebrando-estrutura.html', 'r', 'iso-8859-1') as f:
        return FakeRequest(f.read().encode('iso-8859-1'))


def fake_request_error(*args, **kwargs):
    raise FakeException('Internet Down')


class CepModelTestCase(TestCase):
    def test_can_isntantiate(self):
        cep = Cep(codigo='11111111')
        cep.save()
        self.assertIsInstance(cep, Cep)

    def test_sucessive_saves_increments_id(self):
        cep = Cep(codigo='11111111')
        cep.save()
        novo_cep = Cep(codigo='11111112')
        novo_cep.save()
        self.assertEqual(2, novo_cep.id)

    def test_cep_str(self):
        cep = Cep(codigo='11111111')
        cep.save()
        self.assertEqual('11.111-111', str(cep))


class CepFormTestCase(TestCase):
    def test_invalid_cep_format(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('701150-903')

    def test_invalid_cep_with_only_ones(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('111111111')

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_fail))
    def test_validate_with_correios_invalid_cep(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('71150-903')

    @mock.patch('requests.post',
                mock.Mock(side_effect=fake_request_success_brasilia))
    def test_correctly_cep(self):
        field = CepField()
        self.assertEqual('70.150-903',
                         field.clean('70.150-903').original_value)

    @mock.patch('requests.post',
                mock.Mock(side_effect=fake_request_success_brasilia))
    def test_correctly_cep_with_only_dash(self):
        field = CepField()
        self.assertEqual('70150903',
                         field.clean('70150-903').codigo)

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_error))
    def test_validate_without_internet_silent(self):
        field = CepField(force_correios_validation=False)
        self.assertEqual('70.150-903',
                         field.clean('70.150-903').original_value)

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_error))
    def test_validate_without_internet_raises_exception(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('70.150-903')

    @mock.patch('requests.post',
                mock.Mock(side_effect=iter(fake_request_success_brasilia,
                                           fake_request_error)))
    def test_revalidate_saved_cep(self):
        field = CepField()
        field.clean('70.150-903')
        self.assertEqual('70.150-903',
                         field.clean('70.150-903').original_value)

    @mock.patch('requests.post',
                mock.Mock(side_effect=fake_request_success_brasilia))
    def test_validate_fulfill_module(self):
        field = CepField()
        cep = field.clean('70.150-903')
        self.assertEqual('Zona Cívico-Administrativa', cep.bairro)

    @mock.patch('requests.post',
                mock.Mock(side_effect=fake_request_success_brasilia))
    def test_validate_fulfill_module_logradouro_with_client(self):
        field = CepField()
        cep = field.clean('70.150-903')
        self.assertEqual('SPP  Palácio da Alvorada (Residência'
                         ' Oficial do Presidente da República)',
                         cep.logradouro)

    def test_request_timeout(self):
        cep = CepField(timeout=0.0001)
        with self.assertRaises(ValidationError):
            cep.clean('70.150-903')

    def test_request_timeout_without_raise_error(self):
        cepfield = CepField(force_correios_validation=False, timeout=0.0001)
        cep = cepfield.clean('70.150-903')
        self.assertFalse(cep.valido)


class ParserTestCase(TestCase):
    def setUp(self):
        self.data = {
            'logradouro': 'Rua Doutor Raul Silva',
            'bairro': 'Jardim Francisco Fernandes',
            'cidade': 'São José do Rio Preto',
            'estado': 'SP',
            'complemento': 'de 2301/2302 ao fim',
        }

    def test_parser_gets_bairro(self):
        response = fake_request_success_logradouro()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(self.data['bairro'],
                         parsed_data['bairro'])

    def test_parser_gets_cidade(self):
        response = fake_request_success_logradouro()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(self.data['cidade'],
                         parsed_data['cidade'])

    def test_parser_gets_bairro_com_acento(self):
        data = {
            'logradouro': 'SPP',
            'bairro': 'Zona Cívico-Administrativa',
            'cidade': 'Brasília',
            'estado': 'DF',
        }
        response = fake_request_success_brasilia()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(data['cidade'],
                         parsed_data['cidade'])

    def test_parser_gets_estado(self):
        response = fake_request_success_logradouro()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(self.data['estado'],
                         parsed_data['estado'])

    def test_parser_gets_logradouro(self):
        response = fake_request_success_logradouro()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(self.data['logradouro'],
                         parsed_data['logradouro'])

    def test_parser_gets_complemento(self):
        response = fake_request_success_logradouro()
        parser = Parser(response.content)
        parsed_data = parser.get_data()
        self.assertEqual(self.data['complemento'],
                         parsed_data['complemento'])

    def test_parser_get_all_key(self):
        response = fake_request_success_brasilia()
        parser = Parser(response.content)
        self.assertTrue(parser.get_labels())

    def test_parser_get_all_content(self):
        response = fake_request_success_brasilia()
        parser = Parser(response.content)
        self.assertTrue(parser.get_contents())

    def test_parser_with_cep_desmembrado(self):
        response = fake_request_cep_desmembrado()
        parser = Parser(response.content)
        self.assertTrue(parser.get_contents())


class EngineTestCase(TestCase):

    def test_instantiate_engine(self):
        Engine()

    def test_get_labels_without_data(self):
        engine = Engine()
        self.assertFalse(engine.get_labels())

    def test_get_contents_without_data(self):
        engine = Engine()
        self.assertFalse(engine.get_contents())

    def test_get_data_without_data(self):
        engine = Engine()
        self.assertFalse(engine.get_data())

    def test_busca_dados_not_implemented_raise_error(self):
        engine = Engine()
        with self.assertRaises(NotImplementedError):
            engine.busca_dados()

    def test_configura_conteudo_not_implemented_raise_error(self):
        engine = Engine()
        with self.assertRaises(NotImplementedError):
            engine.configura_conteudo()


class ParserEngineTestCase(TestCase):

    def setUp(self):
        response = fake_request_success_logradouro()
        self.content = response.content.decode('iso-8859-1')

    def test_instantiate_parser_engine(self):
        ParserEngine()

    def test_configura_conteudo_with_success(self):
        engine = ParserEngine()
        engine.configura_conteudo(self.content)
        self.assertIsNotNone(engine.conteudo)

    def test_busca_dados_with_success(self):
        engine = ParserEngine()
        engine.configura_conteudo(self.content)
        engine.busca_dados()
        self.assertIsNotNone(engine.tabela_html)

    def test_busca_dados_with_parser_broken(self):
        engine = ParserEngine()
        engine.configura_conteudo(
            fake_request_fail_parser_quebrado().content.decode('iso-8859-1'))
        with self.assertRaises(ValidationError):
            engine.busca_dados()
