class CartService:
    @staticmethod
    def add_to_cart(session, product_code, name, price, imageUrl, quantity=1):# thêm sản phẩm vào giỏ hàng
        if quantity <= 0:# tránh thêm vào số lượng = 0
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
                cart.pop(product_code)# nếu sản phẩm nhỏ hơn 0 xóa khỏi giỏ hàng
            else:
                cart[product_code]['quantity'] = quantity #lơn hơn cập nhật số lượng
            session['cart'] = cart#lưu vào session
            session.modified = True #đánh dấu phiên đã thay đổi

    @staticmethod
    def remove_from_cart(session, product_code):
        cart = session.get('cart', {})# lấy dữ liệu từ giỏ hàng nếu không có sản phẩm trả về rỗng {}
        cart.pop(product_code, None)#xóa sản phẩm có productcode none giúp không bị báo lỗi khi xóa 1 sản phẩm không tồn tại
        session['cart'] = cart# cập nhật lại session
        session.modified = True

    @staticmethod
    def get_cart(session): # lấy thông tin sản phẩm trong session hiện lên giỏ hàng
        cart = session.get('cart', {})#lấy sản phẩm trong session néu chưa có khởi tạo một dictionary rỗng
        total_price = sum( #sử dụng Generator Expression để tính tông tiền nhanh
            int(item.get('price', 0)) * int(item.get('quantity', 0))
            for item in cart.values()#duyệt qua từng giá trị trong giỏ hàng
            if isinstance(item, dict)#đảm bảo rằng dữ liệu bên trong cart phải là một dictionary thì mới tính toán
        )
        return cart, total_price
