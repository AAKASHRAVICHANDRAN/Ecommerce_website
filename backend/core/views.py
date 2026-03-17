from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .models import Product, Category, Order, UserProfile, OrderItem
from decimal import Decimal
from .serializers import ProductSerializer, CategorySerializer
import stripe

# ---------------------------------------------------------
# Stripe Setup
# ---------------------------------------------------------
stripe.api_key = settings.STRIPE_SECRET_KEY


# ---------------------------------------------------------
# API VIEWSETS
# ---------------------------------------------------------
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# ---------------------------------------------------------
# STRIPE CHECKOUT SESSION (API)
# ---------------------------------------------------------
@api_view(['POST'])
def create_checkout_session(request):
    items = request.data.get('items', [])
    line_items = []

    for it in items:
        price = float(it.get('price', 0))
        quantity = int(it.get('quantity', 1))

        image_url = it.get('image')
        if image_url:
            image_url = request.build_absolute_uri(image_url)

        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': it.get('title'),
                    'images': [image_url] if image_url else [],
                },
                'unit_amount': int(price * 100),
            },
            'quantity': quantity
        })

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=line_items,
            success_url=settings.FRONTEND_URL + '/checkout/success/',
            cancel_url=settings.FRONTEND_URL + '/checkout/cancel/',
        )
        return Response({'id': session.id})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ---------------------------------------------------------
# API — COD Checkout
# ---------------------------------------------------------

@api_view(["POST"])
def checkout_cod(request):
    data = request.data
    items = data.get("items", [])
    customer = data.get("customer", {})

    if not request.user.is_authenticated:
        return Response({"error": "Login required"}, status=403)

    if len(items) == 0:
        return Response({"error": "Cart is empty"}, status=400)

    # COD Fee
    COD_CHARGE = Decimal("30.00")  # you can change

    order = Order.objects.create(
        user=request.user,
        payment_method="cod",
        cod_fee=COD_CHARGE,
        payment_status="pending",

        full_name=customer.get("name"),
        phone=customer.get("phone"),
        email=customer.get("email"),

        address_line1=customer.get("address"),
        city=customer.get("city"),
        state=customer.get("state"),
        postal_code=customer.get("pincode"),
        country="India"
    )

    total = Decimal("0.00")

    for item in items:
        product = Product.objects.get(id=item["id"])
        qty = item["quantity"]
        price = Decimal(str(item["price"]))

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=price
        )

        total += price * qty

    order.total_amount = total + COD_CHARGE
    order.save()

    return Response({
        "success": True,
        "order_id": order.id,
        "total": order.total_amount
    })


# ---------------------------------------------------------
# FRONTEND PAGES
# ---------------------------------------------------------
def landing_page(request):
    return render(request, 'frontend/landing.html')


def index_page(request):
    products = Product.objects.all().order_by('-created_at')[:100]
    return render(request, 'frontend/index.html', {
        'products': products,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def product_page(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'frontend/product.html', {
        'product': product,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


def cart_page(request):
    return render(request, 'frontend/cart.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })


# ---------------------------------------------------------
# SIMPLE CHECKOUT PAGE
# (Single product checkout view)
# ---------------------------------------------------------
@login_required
def checkout_page(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        payment_method = request.POST.get("payment_method")

        # --- COD FLOW ---
        if payment_method == "cod":
            order = Order.objects.create(
                user=request.user,
                ordered=True,
                ordered_at=timezone.now(),
                payment_method="cod",  # store cod
                payment_status="pending",
                full_name=full_name,
                phone=phone,
                address_line1=address,
                postal_code=pincode,
                total_amount=product.price
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
            return redirect("checkout-success")

        # --- ONLINE FLOW ---
        return render(request, "frontend/checkout_payment.html", {
            "product": product,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "full_name": full_name,
            "phone": phone,
            "address": address,
            "pincode": pincode,
        })

    # First visit to checkout
    return render(request, 'frontend/checkout.html', {
        'product': product,
    })


# ---------------------------------------------------------
# SUCCESS & CANCEL
# ---------------------------------------------------------
def success_page(request):
    return render(request, 'frontend/success.html')


def cancel_page(request):
    return render(request, 'frontend/cancel.html')


# ---------------------------------------------------------
# SIGNUP PAGE
# ---------------------------------------------------------
def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        country = request.POST.get("country", "India").strip()
        gender = request.POST.get("gender", "").strip()

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name.split(" ")[0] if full_name else "",
            last_name=" ".join(full_name.split(" ")[1:]) if full_name and len(full_name.split(" ")) > 1 else ""
        )

        UserProfile.objects.create(
            user=user,
            full_name=full_name,
            gender=gender,
            phone=phone,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )

        login(request, user)
        return redirect("profile")

    return render(request, "frontend/signup.html")


# ---------------------------------------------------------
# LOGIN PAGE (Custom)
# ---------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password")
        return redirect("login")

    return render(request, "frontend/login.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
def logout_view(request):
    full_name = ""
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            full_name = request.user.profile.full_name
        else:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()

    logout(request)

    return render(request, 'frontend/logout.html', {
        "full_name": full_name
    })


# ---------------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------------
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "frontend/profile.html", {
        "user": request.user
    })
