from django.db import models
from django.core.validators import MinValueValidator
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
from adm.models import ProductVariant,Coupon


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="House or Company Name")
    postoffice = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# Define the receiver function to create OrderAddress
@receiver(post_save, sender=Address)
def create_order_address(sender, instance, created, **kwargs):
    if created:
        OrderAddress.objects.create(
            user=instance.user,
            name=instance.name,
            postoffice=instance.postoffice,
            street=instance.street,
            city=instance.city,
            state=instance.state,
            country=instance.country,
            pin_code=instance.pin_code,
        )


class OrderAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="House or Company Name")
    postoffice = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now())
    modified_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)  # Add coupon field

    def __str__(self):
        return f"cart for {self.user.username}"


class Cartitem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.username}"


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(OrderAddress, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    order_date = models.DateTimeField(default=datetime.now())
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)   
    total_price_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} on {self.order_date}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_status = models.CharField(
        max_length=20,
        choices=[
            ("Order Placed", "Order Placed"),
            ("Shipped", "Shipped"),
            ("Delivered", "Delivered"),
            ("Cancelled", "Cancelled"),
            ("Return Requested", "Return Requested"),
        ],
        default="Order Placed",
    )
    return_reason = models.TextField(blank=True, null=True)
    refund_added_to_wallet = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"
