# Generated by Django 4.1.2 on 2023-12-13 09:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('egroceryapp', '0010_add_to_cart_subtotal_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount_data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_ordered', models.DateTimeField(auto_now_add=True)),
                ('total_items_placed', models.IntegerField(default=None)),
                ('total_price', models.IntegerField(default=None)),
                ('total_discounted_price', models.IntegerField(default=None)),
                ('grand_total', models.IntegerField(default=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
