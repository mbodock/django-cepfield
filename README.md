# Django CepField

Valida e preenche automaticamente endereço baseado em um numero de CEP.

## Instalação

### Requisitos

* Django 1.7+
* Requests 2.9+

### Instalando


* Instale com o pip:

```shell
pip install django-cepfield
```

* Adicione a App `cep` ao seu `INSTALLED_APPS` localizado em seu settings.
* Crie as tabelas necessárias:

```shell
./manage syncdb
```

## Uso

Crie seu form normalmente:

```python

# seu arquivo de forms
from cep.forms import CepField


class MeuForm(forms.Form):
    cep = CepField()

# sua view
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
