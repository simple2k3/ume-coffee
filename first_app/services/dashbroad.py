from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta, date
from first_app.models import Order, ProductMaster
import calendar

from first_app.models import Categories, TableMaster, StatusMaster

from first_app.models import OrderDetail


class DashboardService:

    @staticmethod
    def get_daily_revenue(month=None, year=None):
        """Doanh thu theo ngày của tháng được chọn (mặc định là tháng hiện tại)."""
        now = timezone.now()
        today = now.date()
        month = month or today.month
        year = year or today.year
        # Xác định số ngày trong tháng
        num_days = calendar.monthrange(year, month)[1]
        # Danh sách nhãn & giá trị
        labels, values = [], []
        for day_num in range(1, num_days + 1):
            current_date = date(year, month, day_num)
            start_of_day = timezone.make_aware(
                timezone.datetime(year, month, day_num, 0, 0, 0)
            )
            end_of_day = start_of_day + timedelta(days=1)
            # Lọc đơn hàng hoàn tất trong ngày đó
            total = (
                Order.objects.filter(
                    status=2,  # 2 = hoàn tất
                    created_at__gte=start_of_day,
                    created_at__lt=end_of_day
                ).aggregate(total_amount=Sum("amount"))["total_amount"] or 0
            )

            labels.append(current_date.strftime("%d/%m"))
            values.append(float(total))

        return {"labels": labels, "values": values}

    @staticmethod
    def get_summary():
        total_orders = Order.objects.filter(status=1).count()
        total_products = ProductMaster.objects.count()
        total_categories = Categories.objects.count()
        total_table = TableMaster.objects.count()
        return {
            "total_orders": total_orders,
            "total_products": total_products,
            "total_categories": total_categories,
            "total_table": total_table,
        }

    @staticmethod
    def get_order_status_data():
        # Thống kê trạng thái đơn hàng
        return {
            "completed": Order.objects.filter(status=2).count(),
            "pending": Order.objects.filter(status=1).count(),
            "cancelled": Order.objects.filter(status=3).count(),
        }

    @staticmethod
    def get_today_revenue(month=None, year=None):
        today = timezone.localdate()
        month = month or today.month
        year = year or today.year

        # Ngày bắt đầu tháng
        start_of_month = timezone.make_aware(timezone.datetime(year, month, 1, 0, 0, 0))

        # Ngày kết thúc tháng
        if month == 12:
            end_of_month = timezone.make_aware(timezone.datetime(year + 1, 1, 1, 0, 0, 0))
        else:
            end_of_month = timezone.make_aware(timezone.datetime(year, month + 1, 1, 0, 0, 0))

        total = (
                Order.objects.filter(
                    status=2,  # Hoàn tất
                    created_at__gte=start_of_month,
                    created_at__lt=end_of_month
                ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        )
        return total

    @staticmethod
    def get_top_selling_products(limit=5):
        # 1. Lấy top sản phẩm theo số lượng bán
        qs = (
            OrderDetail.objects
            .values("product")  # product_code trong OrderDetail
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:limit]
        )
        # 2. Danh sách product_code theo thứ tự
        product_codes_ordered = [item["product"] for item in qs]

        # 3. Lấy thông tin sản phẩm từ ProductMaster
        products = ProductMaster.objects.filter(product_code__in=product_codes_ordered).only(
            "product_code",
            "product_name",
            "imageUrl",
            "price",
        )

        # 4. Map product_code -> total_sold
        sold_map = {item["product"]: item["total_sold"] for item in qs}

        # 5. Chuẩn hóa dữ liệu theo đúng thứ tự top
        product_map = {p.product_code: p for p in products}
        result = []

        for code in product_codes_ordered:
            p = product_map.get(code)
            if p:
                result.append({
                    "code": p.product_code,
                    "name": p.product_name,
                    "image": p.imageUrl if p.imageUrl else None,  # URL trực tiếp
                    "price": p.price,
                    "total_sold": sold_map.get(code, 0),
                })

        return result
