from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
from core.views import checkout_cod, create_checkout_session

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # API Router
    path('', include(router.urls)),

    # Payment Endpoints
    path("checkout-cod/", checkout_cod, name="checkout_cod"),
    path("create-checkout-session/", create_checkout_session, name="create_checkout_session"),
]
