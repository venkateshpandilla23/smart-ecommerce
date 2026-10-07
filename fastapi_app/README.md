# Smart E-Commerce Platform

## Project Overview

This project is a Smart E-Commerce Platform built using FastAPI for the user panel and Django for the admin panel.

The platform provides user authentication, product browsing, cart management, order management, mock payment processing, notifications, email notifications, WebSocket updates, and an admin dashboard with analytics and reports.

FastAPI and Django use the same MySQL database.

---

## Technologies Used

- Python 3.11.3
- FastAPI
- Django
- MySQL
- SQLAlchemy
- PyMySQL
- mysqlclient
- JWT Authentication
- Auth0
- Stripe SDK
- Mock Payment Flow
- WebSockets
- SMTP Email
- Pydantic
- Uvicorn
- Chart.js
- Pillow
- ReportLab

---

# FastAPI User Panel

## Main Features

### User Management

- User registration
- User login
- JWT authentication
- User profile
- Edit profile
- Change password
- Delete account

### Authentication

- JWT-based authentication
- Auth0 login
- Role-based access control
- Customer, Staff, and Admin roles

### Product Management

- View products
- View individual product
- Filter products by category
- Filter products by price
- Sort products by popularity

### Cart Management

- Add products to cart
- View cart
- Update cart quantity
- Remove products from cart
- Clear cart
- Stock validation
- WebSocket cart updates

### Order Management

- Create orders from cart
- View user orders
- View individual orders
- Cancel orders
- Track order status
- Admin order management
- WebSocket order status notifications

### Payment

- Payment API
- Payment records
- Payment success handling
- Payment failure handling
- Mock payment flow for development/testing
- Payment success notifications
- Payment failure notifications

> Note: The current project uses a mock payment flow for development/testing. Live Stripe payment processing is not enabled.

### Notifications

- Create notifications
- View user notifications
- Mark notifications as read
- Payment notifications
- Order status notifications
- WebSocket real-time notifications

### Email

- Payment confirmation emails
- Payment failure emails
- SMTP email integration

### Auth0

- Auth0 login endpoint
- Auth0 callback
- Auth0 user integration with the application database

---

# Django Admin Panel

## Admin Features

### User Management

- Create users
- View users
- Edit users
- Delete users
- Assign user roles
- Search users
- Filter users by role

### Product Management

- Create products
- View products
- Edit products
- Delete products
- Upload product images
- Manage product price and stock
- Filter products by category

### Order Management

- View orders
- Edit orders
- Update order status
- View order items
- Manage order information

### Cart Management

- View cart items
- Manage cart quantity
- View user and product information

### Payment Management

- View payment records
- View order ID
- View user ID
- View amount
- View payment method
- View payment status
- View transaction ID

### Notification Management

- View notifications
- View user ID
- View notification title
- View notification message
- View read/unread status
- View notification creation time

---

# Admin Dashboard

The Django admin dashboard provides:

- Total users
- Total orders
- Total sales
- Low-stock product count
- Order status summary
- Revenue trends
- Top-selling products
- Revenue by order
- Chart-based analytics

Low-stock products are identified when stock is 5 or below.

---

# Reports

The admin panel supports:

- Order CSV export
- Order PDF export

---

# Project Structure

```text
smart-ecommerce/
│
├── fastapi_app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── email_utils.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── venv/
│
├── django_admin/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── admin_panel/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── templates/
│
├── manage.py
├── ecommerce_db.sql
└── ...