from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from accounts.models import Cart, CartItem
from accounts.serializers import CartItemSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from base.utils import CustomPagination

# Create your views here.


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering = ['-id']


class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['$product_name']
    ordering_fields = ['product_name', 'price']

    def get_queryset(self):
        category_uid = self.request.query_params.get('category_uid')
        queryset = Product.objects.filter(category=category_uid)
        return queryset

    def retrieve(self, request, pk):
        product = Product.objects.get(uid=pk)

        if not request.user.is_authenticated:
            productSerializer = ProductSerializer(product, context={"request": request})
            return Response(productSerializer.data)

        cart_item = CartItem.objects.filter(
            cart__user=request.user, product=product)

        isInCart = False
        if cart_item.exists():
            isInCart = True

        productSerializer = ProductSerializer(product, context={"request": request})

        modData = productSerializer.data.copy()
        modData['isInCart'] = isInCart

        return Response(modData)
