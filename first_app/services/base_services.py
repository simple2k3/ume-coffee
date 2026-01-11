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
    #   <!--search-->
    # <form method="get" action="{% url 'search_products' %}" class="search-form d-flex align-items-center me-3">
    #      <input type="text" name="q" class="form-control search-input" placeholder="Tìm kiếm cà phê..." value="{{ request.GET.q|default:'' }}">
    #      <button type="submit" class="btn btn-dark ms-2">
    #        <i class="bi bi-search"></i>
    #      </button>
    # </form>

#     < a href = "#"
#     class ="bell-icon text-dark position-relative dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" >
#     < i
#     class ="bi bi-bell fs-4" > < / i >
#     { % if notification_count > 0 %}
#     < span
#     class ="cart-badge position-absolute top-0 start-100 translate-middle rounded-circle bg-warning text-dark fw-bold" >
#     {{notification_count}}
# < / span >
# { % endif %}
# < / a >