from django.contrib import admin
from .models import Product, ProductImage, Category, Coupon

# Register your models here.
admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=['category_name', 'slug', 'category_image']

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
    list_display=['product_name', 'category', 'slug', 'price', 'product_description', ]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display=['coupon_code', 'discount_amount', 'minimum_amount', 'is_expired']



