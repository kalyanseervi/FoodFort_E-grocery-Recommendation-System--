# com_vis/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, help_text='Required. Enter your mobile number.')
    Address = models.CharField(max_length=100, help_text='Required. Enter address.')
    pincode = models.CharField(max_length=10, blank=True, null=True)
   
    

    def __str__(self):
        return f'{self.user.username} Profile'
    




class Product(models.Model):
    product_name = models.CharField(max_length=255)
    product_price = models.CharField(max_length=255)
    product_image_url = models.CharField(max_length=255)
    product_category = models.CharField(max_length=255)
    product_quantity = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class EcommerceCsv(models.Model):
    order_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    order_dow = models.CharField(max_length=255)
    order_number = models.CharField(max_length=255)
    order_hour_of_day = models.CharField(max_length=255)
    days_since_prior_order = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)
    add_to_cart_order = models.CharField(max_length=255)
    reordered = models.CharField(max_length=255)
    department_id = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    order_id,user_id,order_number,order_dow,order_hour_of_day,days_since_prior_order,product_id,add_to_cart_order,reordered,department_id,department,product_name


class add_To_Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prodcut_Id_Add = models.CharField(max_length=255, default=None)
    quantity = models.IntegerField(default=None)  
    product_price = models.IntegerField(default=None)  
    subtotal_price = models.IntegerField(default=None)  
    added_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):

        self.subtotal_price = int(self.quantity) * int(self.product_price)

        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_items_placed = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    total_discounted_price = models.IntegerField(default=0)
    grand_total = models.IntegerField(default=0)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    products = models.TextField(blank=True, null=True)  # Store product_Id_Add values as a comma-separated string
    product_All_quantity = models.TextField(blank=True, null=True)



class Discount_data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_items_placed = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    total_discounted_price = models.IntegerField(default=0)
    grand_total = models.IntegerField(default=0)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def update_totals(self):
        # Calculate total quantity and total price based on items in the cart
        cart_items = add_To_Cart.objects.filter(user=self.user)
        self.total_items_placed = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        self.total_price = cart_items.aggregate(Sum('subtotal_price'))['subtotal_price__sum'] or 0

        # Calculate discount based on total_price
        if self.total_price > 2000:
            discount_percentage = 0.1
        elif self.total_price > 1000:
            discount_percentage = 0.05
        else:
            discount_percentage = 0

        # Calculate discounted price and grand total
        self.total_discounted_price = self.total_price - (self.total_price * discount_percentage)
        self.grand_total = self.total_discounted_price  # Add any other additional costs if needed

        self.save()


@receiver(post_save, sender=add_To_Cart)
@receiver(post_delete, sender=add_To_Cart)
def update_discount_data(sender, instance, **kwargs):
    # Create or update Discount_data when a new item is added to the cart
    discount_data, created = Discount_data.objects.get_or_create(user=instance.user)
    discount_data.update_totals()



    



