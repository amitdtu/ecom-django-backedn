from .views import CategoryViewSet, ProductViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('category', CategoryViewSet)
router.register('product',ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]