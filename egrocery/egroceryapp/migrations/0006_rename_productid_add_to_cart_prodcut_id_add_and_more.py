# Generated by Django 5.0 on 2023-12-11 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('egroceryapp', '0005_alter_add_to_cart_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='add_to_cart',
            old_name='productID',
            new_name='prodcut_Id_Add',
        ),
        migrations.RemoveField(
            model_name='add_to_cart',
            name='quantity',
        ),
    ]
