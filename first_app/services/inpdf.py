import pdfkit
from django.template.loader import render_to_string
from django.conf import settings

from first_app.services.qr_table_services import TableServices


# from first_app.services.qr_table_services import TableServices
def generate_invoice(order, details):
    qr_url = f"{settings.NGROK_URL}/order-detail/{order.orderId}/"
    qr_base64 = TableServices.generate_qr_base64(qr_url)

    html = render_to_string("admin/invoice.html", {
        "order": order,
        "details": details,
        "qr_base64": qr_base64,
    })
    wk_bin = getattr(settings, "PDFKIT_CONFIG", {}).get("wkhtmltopdf", r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    config = pdfkit.configuration(wkhtmltopdf=wk_bin)
    # trả về bytes
    pdf_bytes = pdfkit.from_string(html, False, configuration=config)
    return pdf_bytes
