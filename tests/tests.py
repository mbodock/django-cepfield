import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(test_dir, os.path.pardir))
os.environ["DJANGO_SETTINGS_MODULE"] = 'tests.settings'

import django
from django.test import TestCase
from django.core.management import call_command
django.setup()
call_command('migrate', '--run-syncdb')

from cep.models import Cep


class CepTestCase(TestCase):
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
