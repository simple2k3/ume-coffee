from django.apps import AppConfig
import threading, time
class FirstAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "first_app"

    def ready(self):
        def delayed_warmup():
            time.sleep(3)
            from .utils.warmup import warmup_ngrok
            warmup_ngrok()
        threading.Thread(target=delayed_warmup, daemon=True).start()