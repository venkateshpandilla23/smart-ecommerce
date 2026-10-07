from django.contrib import admin
from .models import User, Product, Order, OrderItem, Cart, Payment, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "role")
    search_fields = ("name", "email")
    list_filter = ("role",)
    readonly_fields = ("password",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock","image")
    search_fields = ("name", "category")
    list_filter = ("category",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "total_amount", "status")
    search_fields = ("id", "user_id")
    list_filter = ("status",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order_id", "product_id", "quantity", "price")
    search_fields = ("order_id", "product_id")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "product_id", "quantity")
    search_fields = ("user_id", "product_id")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order_id",
        "user_id",
        "amount",
        "payment_method",
        "payment_status",
        "transaction_id",
    )
    search_fields = ("order_id", "user_id", "transaction_id")
    list_filter = ("payment_method", "payment_status")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "title",
        "message",
        "is_read",
        "created_at",
    )
    search_fields = ("user_id", "title", "message")
    list_filter = ("is_read",)