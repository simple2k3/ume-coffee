import qrcode
from io import BytesIO

from django.core.files.base import ContentFile
class TableServices:
    @staticmethod
    def generate_qr_for_table(url):
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        return buffer
    @staticmethod
    def generate_qr_for_order(url):
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        buffer.close()
        return ContentFile(image_bytes, name='order_qr.png')