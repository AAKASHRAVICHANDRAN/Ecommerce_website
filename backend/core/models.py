from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ============================
# CATEGORY MODEL
# ============================
class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ============================
# PRODUCT MODEL
# ============================
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title


# ============================
# ORDER MODEL
# ============================
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(null=True, blank=True)

    # Customer Info
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Shipping
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True, default="India")

    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod")
    payment_status = models.CharField(max_length=20, default="pending")

    cod_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # <-- New
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"



# ============================
# USER PROFILE MODEL
# ============================
class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=120, blank=True, default="India")

    def __str__(self):
        return f"{self.user.username} Profile"


# ============================
# ORDER ITEM MODEL
# ============================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # copy product price at purchase time

    def get_subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"


# ============================
# PAYMENT MODEL
# ============================
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', null=True)
    stripe_payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")  # pending / success / failed
    timestamp = models.DateTimeField(default=timezone.now)

    payment_method = models.CharField(
    max_length=20,
    choices=[("online", "Online"), ("cod", "Cash on Delivery")],
    default="online"
)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
