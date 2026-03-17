from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Landing Page
    path('', core_views.landing_page, name='landing'),

    # Home Product Listing Page
    path('home/', core_views.index_page, name='home'),

    # Product Details
    path('product/<slug:slug>/', core_views.product_page, name='product'),

    # Cart Page
    path('cart/', core_views.cart_page, name='cart'),

    # Checkout (Buy Now)
    path('checkout/<int:pk>/', core_views.checkout_page, name='checkout'),

    # Checkout Status
    path('checkout/success/', core_views.success_page, name='checkout-success'),
    path('checkout/cancel/', core_views.cancel_page, name='checkout-cancel'),

    # ---------------------------
    #      AUTHENTICATION
    # ---------------------------

    # Signup
    path('signup/', core_views.signup_view, name='signup'),

    # Login with custom template
    path('login/', auth_views.LoginView.as_view(
        template_name="frontend/login.html",
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', core_views.logout_view, name='logout'),


    # Profile (requires login)
    path('profile/', core_views.profile_view, name='profile'),

    # Admin Panel
    path('admin/', admin.site.urls),

    # API
    path('api/', include('core.api_urls')),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
