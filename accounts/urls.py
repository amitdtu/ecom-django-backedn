from django.urls import path, include
from .views import RegisterView, LoginView, ActivateAccount,AddToCartView, ValidateCouponView, VerifyPaymentView, ChangeQuantity, OrdersViewSet, CreateOrderView, UserProfileView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('orders', OrdersViewSet, basename='orders')

urlpatterns = [
    path('login', LoginView.as_view(), name='token_obtain_pair'),
    path('login/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register', RegisterView.as_view(), name='auth_register'),
    path('activate/<username>/<email_token>', ActivateAccount.as_view(), name='account_activate'),
    path('cart', AddToCartView.as_view(), name='cart'),
    path('change-quantity', ChangeQuantity.as_view(), name='change_quantity'),
    path('validate-coupon', ValidateCouponView.as_view(), name='validate_coupon'),
    path('create-order', CreateOrderView.as_view(), name='create_order'),
    path('verify-payment', VerifyPaymentView.as_view(), name='verify_coupon'),
    path('user-profile', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),

]