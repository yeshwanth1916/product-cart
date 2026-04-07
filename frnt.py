<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Abandoned Cart System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { text-align: center; color: white; margin-bottom: 40px; }
        h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        nav { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 50px; backdrop-filter: blur(10px); margin-bottom: 20px; }
        nav button { color: white; background: none; border: none; margin: 0 20px; font-weight: bold; font-size: 1.1em; transition: opacity 0.3s; cursor: pointer; }
        nav button:hover, nav button.active { opacity: 0.8; text-decoration: underline; }
        .section { display: none; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .section.active { display: block; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .product-card { border-radius: 20px; padding: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-name { font-size: 1.8em; color: #333; margin-bottom: 10px; }
        .product-price { font-size: 2em; color: #4CAF50; font-weight: bold; margin: 10px 0; }
        .product-category { color: #666; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; margin-bottom: 15px; }
        .add-to-cart { background: linear-gradient(45deg, #FF6B6B, #FF8E8E); color: white; border: none; padding: 15px 30px; font-size: 1.1em; border-radius: 50px; cursor: pointer; transition: transform 0.3s; box-shadow: 0 10px 20px rgba(255,107,107,0.3); }
        .add-to-cart:hover { transform: scale(1.05); }
        .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 1px solid #eee; }
        .delete-btn { background: #f44336; color: white; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; }
        .notification { background: #FFEB3B; color: #333; padding: 20px; border-radius: 15px; margin: 10px 0; border-left: 5px solid #FFC107; }
        .alert { background: #FFEB3B; color: #333; padding: 20px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #FFC107; }
        .success { background: #4CAF50; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; }
        .error { background: #f44336; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; }
        @media (max-width: 768px) { .product-grid { grid-template-columns: 1fr; } h1 { font-size: 2em; } }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛒 Abandoned Cart System</h1>
            <nav>
                <button onclick="showSection('products')" class="active">Products</button>
                <button onclick="showSection('cart')">My Cart</button>
                <button onclick="showSection('notifications')">Notifications</button>
            </nav>
        </header>

        <div id="message"></div>

        <div id="products" class="section active">
            <h2>Available Products</h2>
            <div id="products-list" class="product-grid"></div>
        </div>

        <div id="cart" class="section">
            <h2>My Cart</h2>
            <div id="cart-list"></div>
        </div>

        <div id="notifications" class="section">
            <h2>My Notifications</h2>
            <button onclick="checkAbandonedCarts()" class="add-to-cart" style="margin-bottom: 20px;">Check for Abandoned Carts</button>
            <button onclick="loadNotifications()" class="add-to-cart" style="margin-bottom: 20px; background: #2196F3;">Refresh Notifications</button>
            <div id="notifications-list"></div>
        </div>
    </div>

    <script>
        const userId = 1;
        let currentSection = 'products';

        function showSection(section) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
            document.getElementById(section).classList.add('active');
            document.querySelector(`nav button[onclick="showSection('${section}')"]`).classList.add('active');
            currentSection = section;
            if (section === 'products') loadProducts();
            if (section === 'cart') loadCart();
            if (section === 'notifications') loadNotifications();
        }

        function showMessage(message, type = 'success') {
            const msgDiv = document.getElementById('message');
            msgDiv.innerHTML = `<div class="${type}">${message}</div>`;
            setTimeout(() => msgDiv.innerHTML = '', 5000);
        }

        async function loadProducts() {
            try {
                const response = await fetch('/products');
                const products = await response.json();
                const productsList = document.getElementById('products-list');
                productsList.innerHTML = products.map(product => `
                    <div class="product-card">
                        <h3 class="product-name">${product.name}</h3>
                        <div class="product-category">${product.category}</div>
                        <div class="product-price">$${product.price}</div>
                        <button onclick="addToCart(${product.id})" class="add-to-cart">Add to Cart</button>
                    </div>
                `).join('');
            } catch (error) {
                showMessage('Failed to load products', 'error');
            }
        }

        async function addToCart(productId) {
            try {
                const response = await fetch('/cart/add-to-cart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, product_id: productId, quantity: 1 })
                });
                const result = await response.json();
                if (response.ok) {
                    showMessage('Product added to cart!');
                    if (currentSection === 'cart') loadCart();
                } else {
                    showMessage(result.detail || 'Failed to add to cart', 'error');
                }
            } catch (error) {
                showMessage('Failed to add to cart', 'error');
            }
        }

        async function loadCart() {
            try {
                const response = await fetch(`/cart/${userId}`);
                const cartItems = await response.json();
                const cartList = document.getElementById('cart-list');
                if (cartItems.length === 0) {
                    cartList.innerHTML = '<p>Your cart is empty.</p>';
                } else {
                    cartList.innerHTML = cartItems.map(item => `
                        <div class="cart-item">
                            <div>
                                <h3>${item.product.name}</h3>
                                <p>Quantity: ${item.quantity} - $${item.product.price * item.quantity}</p>
                                <small>Added: ${new Date(item.added_at).toLocaleDateString()}</small>
                            </div>
                            <button onclick="deleteCartItem(${item.id})" class="delete-btn">Delete</button>
                        </div>
                    `).join('');
                }
            } catch (error) {
                showMessage('Failed to load cart', 'error');
            }
        }

        async function deleteCartItem(cartId) {
            try {
                const response = await fetch(`/cart/${cartId}`, { method: 'DELETE' });
                if (response.ok) {
                    showMessage('Item removed from cart!');
                    loadCart();
                } else {
                    showMessage('Failed to remove item', 'error');
                }
            } catch (error) {
                showMessage('Failed to remove item', 'error');
            }
        }

        async function loadNotifications() {
            try {
                const response = await fetch(`/notifications/${userId}`);
                const notifications = await response.json();
                const notificationsList = document.getElementById('notifications-list');
                if (notifications.length === 0) {
                    notificationsList.innerHTML = '<p>No notifications.</p>';
                } else {
                    notificationsList.innerHTML = notifications.map(notification => `
                        <div class="notification">
                            <p>${notification.message}</p>
                            <small>Sent: ${new Date(notification.sent_at).toLocaleDateString()}</small>
                        </div>
                    `).join('');
                }
            } catch (error) {
                showMessage('Failed to load notifications', 'error');
            }
        }

        async function checkAbandonedCarts() {
            try {
                const response = await fetch('/analytics/check-abandoned', { method: 'POST' });
                if (response.ok) {
                    showMessage('Abandoned cart check completed!');
                    loadNotifications();
                } else {
                    showMessage('Failed to check abandoned carts', 'error');
                }
            } catch (error) {
                showMessage('Failed to check abandoned carts', 'error');
            }
        }

        // Load initial data
        loadProducts();
    </script>
</body>
</html>
