import pdfkit
from django.template.loader import render_to_string
from django.conf import settings

def generate_invoice(order, details):
    html = render_to_string("admin/invoice.html", {
        "order": order,
        "details": details
    })

    # nếu bạn đã cấu hình settings.PDFKIT_CONFIG thì dùng settings, nếu không dùng đường dẫn cứng dưới đây
    wk_bin = getattr(settings, "PDFKIT_CONFIG", {}).get("wkhtmltopdf", r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    config = pdfkit.configuration(wkhtmltopdf=wk_bin)

    # trả về bytes
    pdf_bytes = pdfkit.from_string(html, False, configuration=config)
    return pdf_bytes
