from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from base.utils import validate_nonzero
from django.core.validators import MaxValueValidator

# Create your models here.
class Category(BaseModel): 
    category_name  = models.CharField(max_length=100, unique=True)
    slug           = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        return super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name


class Product(BaseModel): 
    category            = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    slug                = models.SlugField(unique=True, null=True, blank=True)
    product_name        = models.CharField(max_length=100)
    product_description = models.TextField()
    price               = models.IntegerField()
    max_quantity        = models.PositiveIntegerField(default=5,validators=[MaxValueValidator(10) ,validate_nonzero] )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        return super(Product, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.product_name

class ProductImage(BaseModel): 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image   = models.ImageField(upload_to='product')
    

class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=20)
    is_expired = models.BooleanField(default=False)
    discount_amount = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


