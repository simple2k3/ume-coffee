# first_app/services/deliveryorder.py
class DeliveryService:
    @staticmethod
    def get_delivery_page(session): #hiện thông tin lên form
        cart = session.get('cart', {})
        products = []
        grand_total = 0
        for code, item in cart.items():
            quantity = int(item.get('quantity', 0))
            price = int(item.get('price', 0))
            total_price = price * quantity
            grand_total += total_price
            products.append({
                'product_name': item.get('name'),
                'quantity': quantity,
                'total_price': total_price,
                'imageUrl': item.get('imageUrl'),
            })
        return products, grand_total


