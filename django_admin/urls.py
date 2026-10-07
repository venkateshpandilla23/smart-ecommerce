from django.contrib import admin
from django.urls import path
from admin_panel.views import dashboard, export_orders_csv, export_orders_pdf

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", dashboard, name="dashboard"),
    path("reports/orders.csv", export_orders_csv, name="export_orders_csv"),
    path("reports/orders.pdf", export_orders_pdf, name="export_orders_pdf"),
]