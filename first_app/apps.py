from django.apps import AppConfig
class FirstAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "first_app"
    def ready(self):
        from .views import warmup_ngrok
        warmup_ngrok()