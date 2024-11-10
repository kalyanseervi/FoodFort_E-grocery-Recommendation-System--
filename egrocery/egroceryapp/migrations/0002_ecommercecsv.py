# Generated by Django 4.1.2 on 2023-12-11 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egroceryapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcommerceCsv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=255)),
                ('user_id', models.CharField(max_length=255)),
                ('order_dow', models.CharField(max_length=255)),
                ('order_number', models.CharField(max_length=255)),
                ('order_hour_of_day', models.CharField(max_length=255)),
                ('days_since_prior_order', models.CharField(max_length=255)),
                ('product_id', models.CharField(max_length=255)),
                ('add_to_cart_order', models.CharField(max_length=255)),
                ('reordered', models.CharField(max_length=255)),
                ('department_id', models.CharField(max_length=255)),
                ('department', models.CharField(max_length=255)),
                ('product_name', models.CharField(max_length=255)),
            ],
        ),
    ]