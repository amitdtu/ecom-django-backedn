from django.shortcuts import render
from django.contrib.auth.models import User
from .serializers import MyTokenObtainPairSerializer, CartSerializer, CartItemSerializer, ProfileSerializer
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Profile, Cart, CartItem
from products.models import Coupon
from products.models import Product
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from base.utils import CustomPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import razorpay
from django.db.models import Count


# Create your views here.

class RegisterView(APIView):
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def post(self, request):

        username = request.data['username']
        email = request.data['email']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        password = request.data['password']
        confirm_password = request.data['confirm_password']

        if User.objects.filter(username=username).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'username already exists'})

        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'email already exists'})

        if password != confirm_password:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'passwords are not same'})

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        token = self.get_tokens_for_user(user)

        return Response(data=token)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ActivateAccount(APIView):
    def get(self, request, username, email_token):
        profile = Profile.objects.get(
            user__username=username, email_token=email_token)

        if profile.is_email_verified:
            return HttpResponse('Your email is already verified.')

        profile.is_email_verified = True
        profile.save()

        if profile:
            return HttpResponse('Your email has been verified.')
        return HttpResponse('Invalid Link.')


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_product(self, product_id):
        try:
            return Product.objects.get(uid=product_id)
        except Product.DoesNotExist:
            raise Response(status=status.HTTP_404_NOT_FOUND, data={
                           'product_id': 'Invalid product_id'})

    def get(self, request):
        cart_item = CartItem.objects.filter(cart__user=request.user)
        serializer = CartItemSerializer(cart_item, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data['product_id']
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)

        product = self.get_product(product_id)

        cart_item = CartItem.objects.filter(cart=cart, product=product)

        if cart_item.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'product_id': 'product_id already exists'})

        cart_item = CartItem.objects.create(cart=cart, product=product)
        cart.save()
        cart_item.save()

        return Response(status=status.HTTP_201_CREATED, data={'detail': f'product added to your card'})

    def delete(self, request):
        product_id = request.data['product_id']
        product = self.get_product(product_id)

        cart_item = CartItem.objects.filter(cart__user=request.user, product=product)

        if not cart_item.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": "Product not found in your cart"})

        cart_item.delete()
        return Response(status=status.HTTP_200_OK, data={'detail': 'product deleted'})
    

class ValidateCouponView(APIView):
    permission_classes = [IsAuthenticated]

    def get_coupon(self, coupon_code):
        try:
            return Coupon.objects.filter(coupon_code=coupon_code).first()
        except Coupon.DoesNotExist:
            raise Response(status=status.HTTP_404_NOT_FOUND, data={
                           'detail': 'Invalid coupon code.'})

    def post(self, request):
        coupon = self.get_coupon(request.data['coupon_code'])

        if coupon is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                           'detail': 'Invalid coupon code.'})

        # cart = Cart.objects.get(user=request.user)

        total_amount = CartItem.objects.filter(
            cart__user=request.user).aggregate(Sum('product__price'))

        if total_amount['product__price__sum'] < coupon.minimum_amount:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': f'You must have at least Rs. {coupon.minimum_amount} order value to avail this coupon'})

        return Response(status=status.HTTP_200_OK, data={'detail': 'Coupon code is valid.', 'discount_amount': coupon.discount_amount})


class ChangeQuantity(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data['product_id']
        quantity = request.data['quantity']

        cart = Cart.objects.get(user=request.user)

        cart_product = CartItem.objects.filter(
            cart=cart, product__uid=product_id).first()

        if not cart_product:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'product_id': 'You does not have this product in your cart'})

        product = Product.objects.get(uid=product_id)

        if product.max_quantity < quantity:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'quantity': f'Cannot buy more than {product.max_quantity} items'})

        if quantity < 1:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'quantity': 'Quantity must be a positive integer'})

        cart_product.quantity = quantity
        cart_product.save()
        return Response(status=status.HTTP_200_OK, data={'quantity': f'Quantity set to {quantity} units'})


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data['razorpay_order_id']
        razorpay_payment_id = request.data['razorpay_payment_id']
        razorpay_signature = request.data['razorpay_signature']

        cart = Cart.objects.get(user=request.user, is_paid = False)
        cart_items = CartItem.objects.filter(cart__user=request.user)

        cart_items.delete()

        try:
            client = razorpay.Client(auth=("rzp_test_wpFpwES54znvGR", "wJQVaIdCB4yQE8B2bCQou6GY"))

            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
                })
            
            cart.is_paid = True
            cart.save()
            
            return Response(data={'status': 'SUCCESS'})
            
        except razorpay.errors.SignatureVerificationError as e:
            return Response(status=status.HTTP_200_OK, data={'status': 'FAILED'})
 

class CreateOrderView(APIView):
    def post(self, request):
        amount = request.data['amount']
        coupon_code = request.data['coupon_code']
        coupon = Coupon.objects.filter(coupon_code=coupon_code).first()

        cart = Cart.objects.filter(user=request.user)


        # cart_items = CartItem.objects.filter(cart=cart)
        cart_items = CartItem.objects.filter(cart__user=request.user)


        total_amount = 0
        for items in cart_items:
            total_amount += items.quantity * items.product.price

        if  not coupon and amount != total_amount or coupon and amount != total_amount - coupon.discount_amount:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'We cannot proceed the this order. Kindly contact with support team ecom@support.com.'})

        if coupon and total_amount < coupon.minimum_amount:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': f'You must have at least Rs. {coupon.minimum_amount} order value to avail this coupon'})


        try:
            client = razorpay.Client(auth=("rzp_test_wpFpwES54znvGR", "wJQVaIdCB4yQE8B2bCQou6GY"))

            DATA = {
                "amount": amount * 100,
                "currency": "INR",
            }
            razorpay_order = client.order.create(data=DATA)

            return Response(data={"razorpay_order": razorpay_order})
        except razorpay.errors.BadRequestError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'order not created'})

class OrdersViewSet(ReadOnlyModelViewSet):
    serializer_class = CartItemSerializer
    pagination_class = PageNumberPagination
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart = Cart.objects.get(user=self.request.user, is_paid=True)
        queryset = CartItem.objects.filter(cart=cart)
        return queryset

class UserProfileView(APIView):
    def get(self, request):
        profile = Profile.objects.get(user=request.user)

        serializer = ProfileSerializer(profile, context={"request": request})

        cart_items_count = 0

        try:
            cart = Cart.objects.get(user=request.user, is_paid=False)
            cart_items_count = CartItem.objects.filter(cart__user=request.user, cart=cart).count()
        except Cart.DoesNotExist:
            pass


        if not profile:
            return Response(data={'detail': 'User not found'})
        
        data = {"profile_image": serializer.data['profile_image'], 'cart_items_count': cart_items_count, **serializer.data['user']}

        return Response(data={'data': data})
