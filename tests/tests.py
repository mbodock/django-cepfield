import os
import mock
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_dir, os.path.pardir))
os.environ["DJANGO_SETTINGS_MODULE"] = 'tests.settings'

import django
from django.test import TestCase
from django.core.management import call_command
from django.core.exceptions import ValidationError
django.setup()
call_command('migrate', '--run-syncdb')

from cep.models import Cep
from cep.forms import CepField


class FakeRequest(object):
    def __init__(self, content):
        self.content = content


def fake_request_success(*args, **kwargs):
    with open('tests/responses/success.html', 'r') as f:
        return FakeRequest(f.read())


def fake_request_fail(*args, **kwargs):
    with open('tests/responses/error.html', 'r') as f:
        return FakeRequest(f.read())


def fake_request_error(*args, **kwargs):
    raise Exception('Internet Down')


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


class CepFormTestCase(TestCase):
    def test_invalid_cep_format(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('701150-903')

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_fail))
    def test_validate_with_correios_invalid_cep(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('71150-903')
            # field.clean('70150-903')  Cep do palacio da alvorada

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_success))
    def test_correctly_cep(self):
        field = CepField()
        self.assertEqual('70.150-903', field.clean('70.150-903'))

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_error))
    def test_validate_without_internet_silent(self):
        field = CepField(raise_exception=False)
        self.assertEqual('70.150-903', field.clean('70.150-903'))

    @mock.patch('requests.post', mock.Mock(side_effect=fake_request_error))
    def test_validate_without_internet_raises_exception(self):
        field = CepField()
        with self.assertRaises(ValidationError):
            field.clean('70.150-903')

    @mock.patch('requests.post', mock.Mock(side_effect=iter(fake_request_success, fake_request_error)))
    def test_revalidade_saved_cep(self):
        field = CepField()
        field.clean('70.150-903')
        self.assertEqual('70.150-903', field.clean('70.150-903'))
