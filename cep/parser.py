# encoding: utf-8
from collections import OrderedDict
from lxml import html

from django.core.exceptions import ValidationError


class Engine(object):

    def __init__(self):
        self.conteudo = None
        self.dados = {}

    def configura_conteudo(self):
        raise NotImplementedError()

    def busca_dados(self):
        raise NotImplementedError()

    def get_labels(self):
        return self.dados.keys()

    def get_contents(self):
        return self.dados.values()

    def get_data(self):
        return self.dados


class ParserEngine(Engine):
    """Engine que o parser irá utilizar"""

    def __init__(self):
        super(ParserEngine, self).__init__()
        self.tabela_html = None

    def configura_conteudo(self, conteudo):
        self.conteudo = html.fromstring(conteudo)

    def busca_dados(self):
        self._busca_tabela()
        self._separa_labels_conteudo()

    def _busca_tabela(self):
        tabela = self.conteudo.find_class('tmptabela')
        if len(tabela[0].getchildren()) > 2:
            raise ValidationError('CEP não encontrado')
        self.tabela_html = tabela[0]

    def _normaliza_dados(self, cabecalho, valor):
        cabecalho = cabecalho.replace(':', '')
        data = OrderedDict(str())
        if 'Localidade' in cabecalho:
            cidade, estado = valor.split('/')
            data['estado'] = estado.strip()
            data['cidade'] = cidade.strip()
        elif 'Logradouro' in cabecalho:
            try:
                logradouro, complemento = valor.split('-')
            except:
                logradouro, complemento = valor, ''
            data['logradouro'] = logradouro.strip()
            data['complemento'] = complemento.strip()
        elif 'Bairro' in cabecalho:
            data['bairro'] = valor.strip()
        else:
            data[cabecalho.lower()] = valor.strip()
        return data

    def _separa_labels_conteudo(self):
        cabecalhos, dados = tuple(
            i.getchildren() for i in self.tabela_html.getchildren()
        )
        for cabecalho, valor in zip(cabecalhos, dados):
            dados_normalizados = self._normaliza_dados(
                cabecalho.text_content(), valor.text_content())
            self.dados.update(dados_normalizados)


class Parser(object):
    def __init__(self, content, engine=ParserEngine()):
        self.content = content.decode('iso-8859-1')
        self.engine = engine

        self.engine.configura_conteudo(self.content)
        self.engine.busca_dados()

    def get_data(self):
        return self.engine.get_data()

    def get_labels(self):
        return self.engine.get_labels()

    def get_contents(self):
        return self.engine.get_contents()
