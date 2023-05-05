from django.contrib import admin
from .models import Profile, Cart, CartItem

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user', 'is_email_verified', 'email_token', 'profile_image']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=['user', 'is_paid', 'cart_items']