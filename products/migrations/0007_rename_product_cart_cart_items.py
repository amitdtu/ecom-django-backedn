# Generated by Django 4.1.6 on 2023-03-31 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_cartitem_alter_cart_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='product',
            new_name='cart_items',
        ),
    ]
