# encoding: utf-8
import re


class Parser(object):
    def __init__(self, content):
        self.content = content
        self.labels = None
        self.contents = None

    def get_data(self):
        self.get_labels()
        self.get_contents()

        return self.format_data()

    def format_data(self):
        data = {}
        for label, value in zip(self.labels, self.contents):
            if 'localidade' in label:
                cidade, estado = value.split('/')
                data['estado'] = estado.strip()
                data['cidade'] = cidade.strip()
            elif 'logradouro' in label and ' - ' in value:
                logradouro, complemento = value.split(' - ', 1)
                data['logradouro'] = logradouro.strip()
                data['complemento'] = complemento.strip()
            else:
                data[label] = value.strip()

        return data

    def get_labels(self):
        matches = re.findall(r'<span class="resposta">(.*?)<\/span>',
                             self.content,
                             re.M | re.I | re.S)
        self.labels = [i.lower().strip(' :') for i in matches]

    def get_contents(self):
        matches = re.findall(r'<span class="respostadestaque">(.*?)<\/span>',
                             self.content,
                             re.M | re.I | re.S)
        self.contents = [re.sub(r'\s+', ' ', i) for i in matches]
