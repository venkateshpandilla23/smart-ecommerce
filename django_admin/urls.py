from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from admin_panel.views import (
    dashboard,
    export_orders_csv,
    export_orders_pdf,
    shop_home,
    login_page,
    cart_page,
    checkout_page,
    orders_page,
    notifications_page,
    profile_page,
    register_page,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", dashboard, name="dashboard"),
    path("reports/orders.csv", export_orders_csv, name="export_orders_csv"),
    path("reports/orders.pdf", export_orders_pdf, name="export_orders_pdf"),
    path("shop/", shop_home, name="shop"),
    path("shop/login/", login_page, name="login"),
    path("shop/cart/", cart_page, name="cart"),
    path("shop/checkout/", checkout_page, name="checkout"),
    path("shop/orders/", orders_page, name="orders"),
    path("shop/notifications/", notifications_page, name="notifications"),
    path("shop/profile/", profile_page, name="profile"),
    path("shop/register/", register_page, name="register"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )