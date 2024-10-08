import csv
from django.core.management.base import BaseCommand
from jcont.models import CNAE  # Ajuste o nome do seu app se necessário

class Command(BaseCommand):
    help = 'Importa dados de CNAE de um arquivo CSV para o banco de dados'

    def handle(self, *args, **kwargs):
        with open('data/cnae.csv', encoding='utf-8') as csvfile:  # Ajuste o caminho para o CSV
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # Criação do registro CNAE sem verificação de duplicatas
                CNAE.objects.create(
                    codigo=row['CNAE'][:10],
                    descricao=row['DESCRIÇÃO'],
                    cod_setor=row.get('CÓD.SETOR'),
                    nome_setor=row.get('NOME SETOR')
                )
        self.stdout.write(self.style.SUCCESS('Dados de CNAE importados com sucesso!'))
