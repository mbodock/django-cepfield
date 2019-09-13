# Django CepField

Valida e preenche automaticamente endereço baseado em um numero de CEP.

## Build Status

[![Build Status](https://travis-ci.org/mbodock/django-cepfield.svg?branch=master)](https://travis-ci.org/mbodock/django-cepfield/)
[![Coverage Status](https://coveralls.io/repos/github/mbodock/django-cepfield/badge.svg?branch=master)](https://coveralls.io/github/mbodock/django-cepfield?branch=master)


## Instalação

### Requisitos

* Django 1.11 para python 2.7
* Django 2.0+ para python 3.5+
* Requests 2.20+


### Instalando


* Instale com o pip:

```shell
pip install django-cepfield
```

* Adicione a App `cep` ao seu `INSTALLED_APPS` localizado em seu settings.
* Crie as tabelas necessárias:

```shell
./manage migrate
```


## Uso

Crie seu form normalmente:

```python

# seu arquivo de forms
from cep.forms import CepField


class MeuForm(forms.Form):
    cep = CepField()
    # CepField(force_correios_validation=False) não irá falhar ao tentar conectar-se aos correios
    # CepField(timeout=3) O padrão é 10s.
    # Você pode usar ambas ao mesmo tempo

# Em sua view
form = MeuForm(request.GET)
if form.is_valid():  # Isso irá salvar o cep se o mesmo for válido
    cep = form.cleaned_data.get('cep')
    return cep.bairro
```

Você também pode acessar diretamente os models:

```python

from cep.models import Cep
cep = Cep.objects.get(codigo='70150903')
print cep.bairro
```
