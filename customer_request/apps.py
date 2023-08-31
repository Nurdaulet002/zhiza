from django.apps import AppConfig

class CustomerRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customer_request'

    def ready(self):
        import customer_request.signals
        from .apscheduler import update_messages_without_rating
        update_messages_without_rating()
