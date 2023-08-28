from django.apps import AppConfig


class RafflePrizesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raffle_prizes'

    def ready(self):
        import raffle_prizes.signals
