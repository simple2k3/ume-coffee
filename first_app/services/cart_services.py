class CartService:
    @staticmethod
    def add_to_cart(session, product_code, name, price, imageUrl, quantity=1):
        if quantity <= 0:
            return
        # Lấy giỏ hàng hiện tại
        cart = session.get('cart', {})

        # Nếu sản phẩm đã có trong giỏ hàng thì tăng số lượng
        if product_code in cart:
            cart[product_code]['quantity'] += quantity
        else:
            # Nếu chưa có thì thêm mới
            cart[product_code] = {
                'name': name,
                'price': int(price),
                'quantity': quantity,
                'imageUrl': imageUrl
            }

        # Lưu lại session
        session['cart'] = cart
        session.modified = True

    @staticmethod
    def update_quantity(session, product_code, quantity):
        cart = session.get('cart', {})
        if product_code in cart:
            if quantity <= 0:
                cart.pop(product_code)
            else:
                cart[product_code]['quantity'] = quantity
            session['cart'] = cart
            session.modified = True
    @staticmethod
    def remove_from_cart(session, product_code):
        cart = session.get('cart', {})
        cart.pop(product_code, None)
        session['cart'] = cart
        session.modified = True

    @staticmethod
    def get_cart(session):
        cart = session.get('cart', {})
        total_price = sum(
            int(item.get('price', 0)) * int(item.get('quantity', 0))
            for item in cart.values()
            if isinstance(item, dict)
        )
        return cart, total_price
