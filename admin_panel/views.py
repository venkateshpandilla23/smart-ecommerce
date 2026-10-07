from django.db.models import Sum, Count
from django.shortcuts import render
from django.http import HttpResponse
import csv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .models import User, Product, Order, OrderItem, Payment

def dashboard(request):
    total_users = User.objects.count()
    total_orders = Order.objects.count()

    total_sales = Payment.objects.filter(
        payment_status="success"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    low_stock_products = Product.objects.filter(
        stock__lte=5
    ).count()

    order_status_summary = Order.objects.values("status").annotate(
        count=Count("id")
    )

    revenue_by_order = Payment.objects.filter(
        payment_status="success"
    ).values(
        "order_id"
    ).annotate(
        revenue=Sum("amount")
    ).order_by("order_id")

    top_selling_products = OrderItem.objects.values(
        "product_id"
    ).annotate(
        total_quantity=Sum("quantity")
    ).order_by("-total_quantity")[:5]

    context = {
    "total_users": total_users,
    "total_orders": total_orders,
    "total_sales": total_sales,
    "low_stock_products": low_stock_products,
    "order_status_summary": order_status_summary,
    "revenue_by_order": revenue_by_order,
    "top_selling_products": top_selling_products,
}
    return render(request, "admin_panel/dashboard.html", context)

def export_orders_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "User ID",
        "Total Amount",
        "Status"
    ])

    orders = Order.objects.all().order_by("id")

    for order in orders:
        writer.writerow([
            order.id,
            order.user_id,
            order.total_amount,
            order.status
        ])

    return response


def export_orders_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="orders_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Orders Report")

    y = height - 90

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Order ID")
    pdf.drawString(120, y, "User ID")
    pdf.drawString(190, y, "Total Amount")
    pdf.drawString(300, y, "Status")

    y -= 20

    pdf.setFont("Helvetica", 10)

    orders = Order.objects.all().order_by("id")

    for order in orders:
        pdf.drawString(50, y, str(order.id))
        pdf.drawString(120, y, str(order.user_id))
        pdf.drawString(190, y, f"₹{order.total_amount}")
        pdf.drawString(300, y, str(order.status))

        y -= 20

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 50

    pdf.save()

    return response

def shop_home(request):
    return render(request, "index.html")

def login_page(request):
    return render(request, "login.html")

def cart_page(request):
    return render(request, "cart.html")

def checkout_page(request):
    return render(request, "checkout.html")

def orders_page(request):
    return render(request, "orders.html")

def notifications_page(request):
    return render(request, "notifications.html")

def profile_page(request):
    return render(request, "profile.html")

def register_page(request):
    return render(request, "register.html")