import unicodedata
from first_app.models import ProductMaster
class SearchService:
    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # loại bỏ các dấu
        text_no_accents = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return text_no_accents.lower()
    @staticmethod
    def search_products(query: str):
        """
        Tìm kiếm sản phẩm theo tên:
        - Nếu query để trống, trả về tất cả sản phẩm
        - Nếu query có hoặc không dấu, vẫn tìm được sản phẩm tương ứng
        """
        if not query:
            return ProductMaster.objects.all()
        # Chuẩn hóa query để so sánh
        normalized_query = SearchService.normalize_text(query)
        # Lấy tất cả sản phẩm
        all_products = ProductMaster.objects.all()
        # Lọc những sản phẩm mà tên chứa query
        matched_products = []
        for product in all_products:
            name_normalized = SearchService.normalize_text(product.product_name)
            name_original = product.product_name.lower()
            if normalized_query in name_normalized or query.lower() in name_original:
                matched_products.append(product)

        return matched_products
