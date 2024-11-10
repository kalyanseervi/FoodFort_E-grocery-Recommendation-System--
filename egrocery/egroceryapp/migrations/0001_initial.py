# Generated by Django 5.0 on 2023-12-09 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('product_price', models.CharField(max_length=255)),
                ('product_image_url', models.CharField(max_length=255)),
                ('product_category', models.CharField(max_length=255)),
                ('product_quantity', models.CharField(max_length=255)),
            ],
        ),
    ]