from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(
    max_length=20,
    choices=[
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    ],
    default="customer"
)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return f"{self.name} ({self.email})"

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    class Meta:
        managed = False
        db_table = "products"

    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    total_amount = models.FloatField()
    status = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = "orders"

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = "order_items"

    def __str__(self):
        return f"Order {self.order_id} - Product {self.product_id}"

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = "cart"

    def __str__(self):
        return f"Cart #{self.id}"

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = models.IntegerField()
    user_id = models.IntegerField()
    amount = models.FloatField()
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = "payments"

    def __str__(self):
        return f"Payment #{self.id}"

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(null=True)
    created_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = "notifications"

    def __str__(self):
        return f"Notification #{self.id}"