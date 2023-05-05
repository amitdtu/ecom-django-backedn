# Generated by Django 4.1.6 on 2023-04-02 17:38

import base.utils
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_product_max_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='max_quantity',
            field=models.PositiveIntegerField(default=5, validators=[django.core.validators.MaxValueValidator(10), base.utils.validate_nonzero]),
        ),
    ]