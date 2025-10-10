from django.apps import AppConfig


class NayaSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'naya_site'


class OrcamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orcamentos'
    verbose_name = 'Sistema de Orçamentos'

    def ready(self):
        import signals
