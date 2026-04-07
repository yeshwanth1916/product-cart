import streamlit as st
import requests
import json
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000"

# Session state for authentication
if 'token' not in st.session_state:
    st.session_state.token = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Page configuration
st.set_page_config(
    page_title="Abandoned Cart System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e86c1;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #bee5eb;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_api_request(method, endpoint, data=None, auth_required=True):
    """Make API request and handle response"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {}
        if auth_required and st.session_state.token:
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            return {"error": "Unsupported method"}

        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def login_user(username, password):
    """Login user and get token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]

            # Get user info
            user_response = make_api_request("GET", "/users/me")
            if "error" not in user_response:
                st.session_state.current_user = user_response
                return True
            else:
                st.session_state.token = None
                return False
        else:
            return False
    except:
        return False

def logout_user():
    """Logout user"""
    st.session_state.token = None
    st.session_state.current_user = None

def register_user(username, email, password):
    """Register a new user"""
    response = make_api_request("POST", "/register", {
        "username": username,
        "email": email,
        "password": password
    }, auth_required=False)
    return response

def display_api_response(response, success_message=""):
    """Display API response with appropriate styling"""
    if "error" in response:
        st.markdown(f'<div class="error-message">❌ {response["error"]}</div>', unsafe_allow_html=True)
        return False
    else:
        if success_message:
            st.markdown(f'<div class="success-message">✅ {success_message}</div>', unsafe_allow_html=True)
        return True

# Sidebar navigation
st.sidebar.title("🛒 Abandoned Cart System")

# Authentication section
if st.session_state.current_user:
    st.sidebar.success(f"Logged in as: {st.session_state.current_user['username']}")
    if st.sidebar.button("Logout"):
        logout_user()
        st.experimental_rerun()
else:
    st.sidebar.warning("Not logged in")

st.sidebar.markdown("---")

# Navigation menu
if st.session_state.current_user:
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Users", "Products", "My Cart", "Orders", "Abandoned Carts"]
    )
else:
    page = st.sidebar.radio(
        "Navigation",
        ["Login", "Register"]
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### API Status")
try:
    response = requests.get(f"{API_BASE_URL}/docs")
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Not Responding")
except:
    st.sidebar.error("❌ Cannot Connect to API")

# Main content
st.markdown('<div class="main-header">Abandoned Cart Management System</div>', unsafe_allow_html=True)

if page == "Login":
    st.markdown('<div class="section-header">🔐 Login</div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")
        if submitted:
            if username and password:
                if login_user(username, password):
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please fill in all fields")

elif page == "Register":
    st.markdown('<div class="section-header">📝 Register</div>', unsafe_allow_html=True)

    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submitted = st.form_submit_button("Register")
        if submitted:
            if username and email and password:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    response = register_user(username, email, password)
                    if "error" not in response:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {response['error']}")
            else:
                st.error("Please fill in all fields")

elif not st.session_state.current_user:
    st.warning("Please login to access the application.")
    st.stop()

elif page == "Dashboard":
    st.markdown('<div class="section-header">📊 Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    # Get stats
    users = make_api_request("GET", "/users/")
    products = make_api_request("GET", "/products/")
    carts = make_api_request("GET", "/carts/")
    abandoned = make_api_request("GET", "/carts/abandoned/")
    orders = make_api_request("GET", "/orders/")

    with col1:
        st.metric("Total Users", len(users) if not "error" in users else 0)

    with col2:
        st.metric("Total Products", len(products) if not "error" in products else 0)

    with col3:
        st.metric("Active Carts", len([c for c in carts if not "error" in carts and c.get("status") == "active"]) if not "error" in carts else 0)

    with col4:
        st.metric("Abandoned Carts", len(abandoned) if not "error" in abandoned else 0)

    st.markdown("---")

    # Recent activity
    st.subheader("Recent Orders")
    if not "error" in orders and orders:
        for order in orders[-5:]:  # Show last 5 orders
            st.write(f"Order #{order['id']} - ${order['total_amount']:.2f} - {order['created_at'][:10]}")
    else:
        st.info("No orders found")

elif page == "Users":
    st.markdown('<div class="section-header">👥 User Management</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Create User", "View Users"])

    with tab1:
        st.subheader("Create New User")
        with st.form("create_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")

            submitted = st.form_submit_button("Create User")
            if submitted:
                if username and email:
                    response = make_api_request("POST", "/users/", {"username": username, "email": email})
                    display_api_response(response, "User created successfully!")
                else:
                    st.error("Please fill in all fields")

    with tab2:
        st.subheader("All Users")
        users = make_api_request("GET", "/users/")
        if display_api_response(users):
            if users:
                for user in users:
                    st.write(f"**ID:** {user['id']} | **Username:** {user['username']} | **Email:** {user['email']}")
            else:
                st.info("No users found")

elif page == "Products":
    st.markdown('<div class="section-header">📦 Product Management</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Create Product", "View Products", "Products in Abandoned Carts"])

    with tab1:
        st.subheader("Create New Product")
        with st.form("create_product_form"):
            name = st.text_input("Product Name")
            price = st.number_input("Price", min_value=0.01, step=0.01)
            description = st.text_area("Description")

            submitted = st.form_submit_button("Create Product")
            if submitted:
                if name and price > 0:
                    response = make_api_request("POST", "/products/", {
                        "name": name,
                        "price": price,
                        "description": description
                    })
                    display_api_response(response, "Product created successfully!")
                else:
                    st.error("Please fill in all required fields")

    with tab2:
        st.subheader("All Products")
        products = make_api_request("GET", "/products/")
        if display_api_response(products):
            if products:
                for product in products:
                    st.write(f"**ID:** {product['id']} | **Name:** {product['name']} | **Price:** ${product['price']:.2f}")
                    st.write(f"**Description:** {product['description']}")
                    st.markdown("---")
            else:
                st.info("No products found")

    with tab3:
        st.subheader("Products in Abandoned Carts")
        
        # Get all abandoned carts
        abandoned_carts = make_api_request("GET", "/carts/abandoned/")
        
        if display_api_response(abandoned_carts):
            if abandoned_carts and "error" not in abandoned_carts:
                # Collect product statistics
                product_stats = {}
                total_quantity = 0
                total_value = 0
                
                for cart in abandoned_carts:
                    for item in cart['items']:
                        product_id = item['product_id']
                        product_name = item['product_name']
                        product_price = item['price']
                        quantity = item['quantity']
                        
                        if product_id not in product_stats:
                            product_stats[product_id] = {
                                'name': product_name,
                                'price': product_price,
                                'total_quantity': 0,
                                'total_value': 0,
                                'carts': []
                            }
                        
                        product_stats[product_id]['total_quantity'] += quantity
                        product_stats[product_id]['total_value'] += quantity * product_price
                        product_stats[product_id]['carts'].append({
                            'cart_id': cart['id'],
                            'quantity': quantity,
                            'user_id': cart['user_id'],
                            'username': cart['username'],
                            'days_old': (datetime.now() - datetime.fromisoformat(cart['updated_at'].replace('Z', '+00:00'))).days
                        })
                        
                        total_quantity += quantity
                        total_value += quantity * product_price
                
                if product_stats:
                    st.write(f"**Total Products in Abandoned Carts:** {len(product_stats)}")
                    st.write(f"**Total Units:** {total_quantity}")
                    st.write(f"**Total Value:** ${total_value:.2f}")
                    st.divider()
                    
                    for product_id in sorted(product_stats.keys()):
                        product = product_stats[product_id]
                        
                        with st.expander(f"📦 {product['name']} (${product['price']:.2f})"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Unit Price", f"${product['price']:.2f}")
                            
                            with col2:
                                st.metric("Total Quantity", f"{product['total_quantity']} units")
                            
                            with col3:
                                st.metric("Total Value", f"${product['total_value']:.2f}")
                            
                            st.write(f"**Found in {len(product['carts'])} abandoned cart(s):**")
                            
                            for cart_info in product['carts']:
                                st.write(f"  • **Cart {cart_info['cart_id']}** - {cart_info['quantity']}x ({cart_info['days_old']} days old)")
                                st.write(f"    User: {cart_info['username']} | Value: ${cart_info['quantity'] * product['price']:.2f}")
                else:
                    st.info("No products found in abandoned carts")
            else:
                st.info("No abandoned carts found")

elif page == "My Cart":
    st.markdown('<div class="section-header">🛒 My Cart</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Add to Cart", "View My Cart"])

    with tab1:
        st.subheader("Add Item to Cart")
        with st.form("add_to_cart_form"):
            product_id = st.number_input("Product ID", min_value=1, step=1)
            quantity = st.number_input("Quantity", min_value=1, step=1)

            submitted = st.form_submit_button("Add to Cart")
            if submitted:
                response = make_api_request("POST", f"/carts/{st.session_state.current_user['id']}/items/", {
                    "product_id": product_id,
                    "quantity": quantity
                })
                if display_api_response(response, "Item added to cart successfully!"):
                    st.json(response)

    with tab2:
        st.subheader("My Cart & Abandoned Carts")
        
        # Get user's carts
        user_carts = make_api_request("GET", f"/carts/user/{st.session_state.current_user['id']}")
        
        # Get abandoned carts (show all)
        abandoned_carts = make_api_request("GET", "/carts/abandoned/")
        
        all_carts = []
        
        # Add user's carts
        if display_api_response(user_carts):
            if user_carts and "error" not in user_carts:
                all_carts.extend([(cart, "User Cart") for cart in user_carts])
        
        # Add abandoned carts
        if display_api_response(abandoned_carts):
            if abandoned_carts and "error" not in abandoned_carts:
                all_carts.extend([(cart, "Abandoned Cart") for cart in abandoned_carts])
        
        if all_carts:
            st.write(f"**Total Carts Found:** {len(all_carts)}")
            st.divider()
            
            for cart, cart_type in all_carts:
                # Color code for cart type
                if cart_type == "Abandoned Cart":
                    status_color = "🚨"
                else:
                    status_color = "🛒"
                
                with st.expander(f"{status_color} {cart_type} #{cart['id']} ({cart['status']}) - {cart.get('username', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Total:** ${cart['total_amount']:.2f}")
                        st.write(f"**Status:** {cart['status'].upper()}")
                        st.write(f"**Type:** {cart_type}")
                    
                    with col2:
                        st.write(f"**Created:** {cart['created_at'][:10]}")
                        st.write(f"**Updated:** {cart['updated_at'][:10]}")
                        if cart_type == "Abandoned Cart":
                            days_old = (datetime.now() - datetime.fromisoformat(cart['updated_at'].replace('Z', '+00:00'))).days
                            st.write(f"**Days Old:** {days_old} days")

                    st.divider()
                    
                    if cart['items']:
                        st.write("**Items in Cart:**")
                        items_df_data = []
                        for item in cart['items']:
                            subtotal = item['quantity'] * item['price']
                            items_df_data.append({
                                'Product': item['product_name'],
                                'Quantity': item['quantity'],
                                'Unit Price': f"${item['price']:.2f}",
                                'Subtotal': f"${subtotal:.2f}"
                            })
                        
                        for item in cart['items']:
                            st.write(f"- {item['product_name']} (x{item['quantity']}) @ ${item['price']:.2f} each")
                    else:
                        st.write("*No items in cart*")
                    
                    # Action buttons for abandoned carts
                    if cart_type == "Abandoned Cart":
                        st.divider()
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Create Order #{cart['id']}", key=f"order_{cart_type}_{cart['id']}"):
                                response = make_api_request("POST", "/orders/", {"cart_id": cart['id']})
                                display_api_response(response, "Order created successfully!")
                        with col2:
                            st.info("💡 Consider recovery campaign for this cart")
        else:
            st.info("No carts found")

elif page == "Orders":
    st.markdown('<div class="section-header">📋 My Orders</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Create Order", "View My Orders"])

    with tab1:
        st.subheader("Create Order from Cart")
        # Get user's active carts
        carts = make_api_request("GET", f"/carts/user/{st.session_state.current_user['id']}")
        if "error" not in carts and carts:
            active_carts = [cart for cart in carts if cart['status'] == 'active']
            if active_carts:
                cart_options = {f"Cart #{cart['id']} - ${cart['total_amount']:.2f}": cart['id'] for cart in active_carts}
                selected_cart = st.selectbox("Select Cart to Order", list(cart_options.keys()))

                if st.button("Create Order"):
                    cart_id = cart_options[selected_cart]
                    response = make_api_request("POST", "/orders/", {"cart_id": cart_id})
                    display_api_response(response, "Order created successfully!")
            else:
                st.info("No active carts found")
        else:
            st.info("No carts found")

    with tab2:
        st.subheader("My Orders")
        orders = make_api_request("GET", "/orders/")
        if display_api_response(orders):
            # Filter orders for current user (we'd need to add user filtering to API)
            # For now, show all orders but note this should be filtered
            if orders:
                st.warning("Note: Currently showing all orders. API should be updated to filter by user.")
                for order in orders:
                    st.write(f"**Order ID:** {order['id']} | **Cart ID:** {order['cart_id']} | **Total:** ${order['total_amount']:.2f} | **Date:** {order['created_at'][:10]}")
            else:
                st.info("No orders found")

elif page == "Abandoned Carts":
    st.markdown('<div class="section-header">🚨 Abandoned Carts</div>', unsafe_allow_html=True)

    st.subheader("Carts Abandoned for More Than 12 Days")

    if st.button("Refresh Abandoned Carts"):
        abandoned_carts = make_api_request("GET", "/carts/abandoned/")
        if display_api_response(abandoned_carts):
            if abandoned_carts:
                st.markdown(f'<div class="info-message">Found {len(abandoned_carts)} abandoned carts</div>', unsafe_allow_html=True)

                for cart in abandoned_carts:
                    with st.expander(f"Abandoned Cart #{cart['id']} - {cart['username']}"):
                        st.write(f"**Total Value:** ${cart['total_amount']:.2f}")
                        st.write(f"**Last Updated:** {cart['updated_at'][:19]}")
                        st.write(f"**Days Since Update:** {(datetime.now() - datetime.fromisoformat(cart['updated_at'].replace('Z', '+00:00'))).days}")

                        if cart['items']:
                            st.write("**Items:**")
                            for item in cart['items']:
                                st.write(f"- {item['product_name']} (x{item['quantity']}) - ${item['price']:.2f} each")
                        else:
                            st.write("No items in cart")

                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Create Order for Cart #{cart['id']}", key=f"order_{cart['id']}"):
                                response = make_api_request("POST", "/orders/", {"cart_id": cart['id']})
                                display_api_response(response, "Order created from abandoned cart!")
                        with col2:
                            if st.button(f"Mark as Active #{cart['id']}", key=f"active_{cart['id']}"):
                                st.info("Feature not implemented in API yet")
            else:
                st.success("No abandoned carts found!")
    else:
        st.info("Click 'Refresh Abandoned Carts' to load current abandoned carts")

# Footer
st.markdown("---")
st.markdown("*Abandoned Cart System - Built with FastAPI & Streamlit*")