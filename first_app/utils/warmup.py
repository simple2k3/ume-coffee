import requests, time
from django.conf import settings
def warmup_ngrok():
    urls = [
        "static/assets/css/main.css",
        "static/assets/vendor/bootstrap/css/bootstrap.min.css",
    ]

    ngrok = getattr(settings, "NGROK_URL", None)
    if not ngrok:
        print(" Không có NGROK_URL trong settings — bỏ qua warmup.")
        return

    for url in urls:
        full_url = f"{ngrok}/{url.lstrip('/')}"
        try:
            response = requests.get(full_url, timeout=5)
            print(f" Warmup OK: {full_url} ({response.status_code})")
            time.sleep(0.3)
        except Exception as e:
            print(f"⚠Warmup FAIL: {full_url} ({e})")
