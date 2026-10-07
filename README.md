# 🛒 Smart E-Commerce Platform

A full-stack e-commerce platform built using **FastAPI, Django, MySQL, HTML, CSS, and JavaScript**.

The project provides a customer-facing shopping experience through FastAPI APIs and a responsive web interface, along with a Django-based admin panel for managing users, products, orders, payments, notifications, and analytics.

---

## 📌 Project Overview

The Smart E-Commerce Platform allows customers to:

- Register and log in
- Browse products
- Filter products by category and price
- Sort products by popularity
- Add products to cart
- Update and remove cart items
- Place orders
- Make mock payments
- View order history and status
- Receive notifications
- Receive email notifications
- Manage their profile

Administrators can:

- Manage users
- Manage products
- Upload product images
- Manage orders
- Manage payments
- Manage notifications
- View sales analytics
- View revenue trends
- View top-selling products
- Monitor low-stock products
- Export order reports as CSV and PDF

---

## 🚀 Technologies Used

### Backend

- Python
- FastAPI
- Django
- SQLAlchemy
- MySQL
- JWT Authentication
- Pydantic

### Frontend

- HTML5
- CSS3
- JavaScript
- Responsive Web Design

### Authentication

- JWT Authentication
- Role-Based Access Control (RBAC)
- Auth0 Integration
- Google Login through Auth0

### Other Features

- WebSocket real-time notifications
- Email notifications
- Mock payment processing
- Postman API testing
- Chart.js analytics dashboard

---

## 🏗️ Project Architecture

```text
Smart E-Commerce Platform
│
├── Customer Frontend
│   └── HTML + CSS + JavaScript
│
├── FastAPI
│   ├── Authentication
│   ├── Products
│   ├── Cart
│   ├── Orders
│   ├── Payments
│   ├── Notifications
│   ├── WebSockets
│   └── Auth0
│
├── Django Admin
│   ├── User Management
│   ├── Product Management
│   ├── Order Management
│   ├── Payment Management
│   ├── Notification Management
│   └── Analytics Dashboard
│
└── MySQL Database


smart-ecommerce/
│
├── admin_panel/
│   └── Django admin dashboard and management views
│
├── django_admin/
│   └── Django project configuration
│
├── fastapi_app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── email_utils.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── profile.html
│   ├── notifications.html
│   ├── css/
│   └── js/
│
├── media/
│   └── products/
│
├── postman/
│   └── Smart E-Commerce Platform API.postman_collection.json
│
├── screenshots/
│   ├── admin/
│   ├── api/
│   └── customer/
│
├── ecommerce_db.sql
├── manage.py
├── .gitignore
└── README.md



