from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, create_checkout_session
from django.urls import path, include

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('create-checkout-session/', create_checkout_session, name='create-checkout-session'),
]
