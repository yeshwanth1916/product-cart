🛒 Abandoned Cart Recovery & Recommendation System

🚀 Overview

This project is a full-stack system designed to track abandoned carts, generate personalized recommendations, and encourage users to complete purchases.

It simulates a real-world e-commerce backend with intelligent cart tracking and recommendation logic.

---

🎯 Problem Statement

In e-commerce platforms, users often add products to their cart but leave without completing the purchase. This leads to lost revenue.

This system solves that problem by:

- Detecting abandoned carts automatically
- Generating relevant product recommendations
- Triggering recovery actions (notifications, suggestions)

---

🧠 Key Features

👤 User Features

- User Signup & Login (JWT Authentication)
- Add / Remove products from cart
- View cart items
- Get personalized product recommendations

🛠️ Admin Features

- View abandoned carts
- Track conversion rate
- Manage products (Add / Update / Delete)

🤖 System Features

- Automatic abandoned cart detection
- Recommendation engine (score-based)
- Background job processing
- Notification trigger system (email/SMS ready)

---

🏗️ System Architecture

Frontend (React.js)
⬇
Backend API (Spring Boot / .NET)
⬇
Business Logic Layer
⬇
Database (SQL)
⬇
Background Jobs (Scheduler)
⬇
Notification Service

---

🗄️ Database Design

Users

- user_id (PK)
- name
- email
- password_hash
- created_at

Products

- product_id (PK)
- name
- price
- category
- stock

Cart

- cart_id (PK)
- user_id (FK)
- status (active / abandoned / ordered)
- last_updated_at

Cart_Items

- cart_item_id (PK)
- cart_id (FK)
- product_id (FK)
- quantity

Orders

- order_id (PK)
- user_id (FK)
- total_price
- created_at

Order_Items

- order_item_id (PK)
- order_id (FK)
- product_id (FK)
- quantity
- price

Recommendations

- rec_id (PK)
- user_id (FK)
- product_id (FK)
- score
- reason

---

🔌 API Endpoints

🔐 Auth

- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/profile

🛍️ Products

- GET /api/products
- GET /api/products/{id}
- GET /api/products?category=

🛒 Cart

- POST /api/cart/add
- PUT /api/cart/update-quantity
- DELETE /api/cart/remove/{productId}
- GET /api/cart
- PUT /api/cart/refresh

🚨 Abandoned Cart

- GET /api/cart/abandoned (Admin)
- POST /api/cart/recover

💳 Orders

- POST /api/orders/place
- GET /api/orders
- GET /api/orders/{id}

🎯 Recommendations

- GET /api/recommendations/{userId}

🛠️ Admin

- GET /api/admin/abandoned-carts
- GET /api/admin/conversion-rate
- POST /api/admin/products
- PUT /api/admin/products/{id}
- DELETE /api/admin/products/{id}

---

⚙️ Abandoned Cart Logic

A cart is marked as abandoned when:

- No activity is detected for a defined threshold (e.g., 30 minutes)

Implementation:

- Track "last_updated_at" in Cart table
- Background job runs periodically
- If current_time - last_updated_at > threshold → mark as abandoned

---

🎯 Recommendation Logic

Products are ranked using a scoring system:

- +5 → Same category
- +3 → Frequently bought together
- +2 → Trending products
- +1 → Discounted items

Top N products are returned based on score.

---

⏱️ Background Jobs

Scheduled tasks:

- Detect abandoned carts
- Generate recommendations
- Trigger notifications

---

📩 Notification System

When a cart is abandoned:

- Send reminder email/SMS
- Include recommended products
- Encourage checkout completion

---

🧪 Tech Stack

- Frontend: React.js
- Backend: Spring Boot / .NET
- Database: MySQL / PostgreSQL
- Authentication: JWT
- Scheduler: Cron Jobs
- Optional: Redis (caching), Kafka (async processing)

---

📈 Future Enhancements

- Machine Learning-based recommendation engine
- Real-time analytics dashboard
- A/B testing for recommendation strategies
- Push notifications integration

---

💀 Key Learnings

- Designing scalable backend systems
- Handling real-world e-commerce scenarios
- Implementing background processing
- Building recommendation engines

---

📌 Conclusion

This project demonstrates how to design a production-like system that improves user engagement and increases conversion rates using smart backend logic.

---

