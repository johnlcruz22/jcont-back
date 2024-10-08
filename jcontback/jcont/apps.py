from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_levels(sender, **kwargs):
    from jcont.models import Nivel
    Nivel.objects.get_or_create(descricao='iniciante')
    Nivel.objects.get_or_create(descricao='habilitado')
    Nivel.objects.get_or_create(descricao='especialista')

def create_default_access_types(sender, **kwargs):
    from jcont.models import TipoAcesso
    TipoAcesso.objects.get_or_create(descricao='master')
    TipoAcesso.objects.get_or_create(descricao='comum')
    TipoAcesso.objects.get_or_create(descricao='técnico')

class JcontConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jcont'

    def ready(self):
        post_migrate.connect(create_default_levels, sender=self)
        post_migrate.connect(create_default_access_types, sender=self)    