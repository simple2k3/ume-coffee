from django.shortcuts import get_object_or_404
from first_app.models import ProductMaster

class CartService:
    @staticmethod
    def get_cart(session):
        cart = session.get('cart', {})
        products = []
        total_price = 0

        for product_code, quantity in cart.items():
            product = get_object_or_404(ProductMaster, product_code=product_code)
            product.quantity = quantity
            product.total_price = quantity * product.price
            total_price += product.price
            products.append(product)

        return products, total_price

    @staticmethod
    def add_to_cart(session, product_code, quantity=1):
        cart = session.get('cart', {})
        cart[product_code] = quantity
        session['cart'] = cart

    @staticmethod
    def remove_from_cart(session, product_code):
        cart = session.get('cart', {})
        if product_code in cart:
            del cart[product_code]
            session['cart'] = cart

    @staticmethod
    def clear_cart(session):
        session['cart'] = {}
