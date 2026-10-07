from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime



class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str


class UserUpdate(BaseModel):
    name: str
    email: EmailStr


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


# ============================================================
# PRODUCT SCHEMAS
# ============================================================

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str


# ============================================================
# CART SCHEMAS
# ============================================================

class CartCreate(BaseModel):
    product_id: int
    quantity: int


class CartUpdate(BaseModel):
    quantity: int


# ============================================================
# ORDER SCHEMAS
# ============================================================

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_amount: float
    status: str
    items: list[OrderItemResponse]


# ============================================================
# ADMIN ORDER STATUS SCHEMA
# ============================================================

class OrderStatusUpdate(BaseModel):
    status: str


# ============================================================
# PAYMENT SCHEMAS
# ============================================================

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str = "stripe"
    payment_status: str = "success"


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    user_id: int
    amount: float
    payment_method: str
    payment_status: str
    transaction_id: str | None = None

class NotificationCreate(BaseModel):
    title: str
    message: str


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime