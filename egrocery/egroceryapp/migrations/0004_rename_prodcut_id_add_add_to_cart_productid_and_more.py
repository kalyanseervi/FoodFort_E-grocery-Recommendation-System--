# Generated by Django 5.0 on 2023-12-11 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egroceryapp', '0003_add_to_cart'),
    ]

    operations = [
        migrations.RenameField(
            model_name='add_to_cart',
            old_name='prodcut_Id_Add',
            new_name='productID',
        ),
        migrations.AddField(
            model_name='add_to_cart',
            name='quantity',
            field=models.CharField(default=None, max_length=255),
        ),
    ]