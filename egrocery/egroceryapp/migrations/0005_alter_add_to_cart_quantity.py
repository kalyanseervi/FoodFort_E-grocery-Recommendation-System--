# Generated by Django 5.0 on 2023-12-11 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egroceryapp', '0004_rename_prodcut_id_add_add_to_cart_productid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add_to_cart',
            name='quantity',
            field=models.CharField(default=1, max_length=255),
        ),
    ]