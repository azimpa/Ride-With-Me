from typing import Any
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class AdmCategories(models.Model):
    name = models.CharField(max_length=50, unique=True)
    offer_type = models.CharField(max_length=50, null=True, blank=True,)
    is_active = models.BooleanField(default=True)  # New field for soft delete

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)  # New field for soft delete

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)  # New field for soft delete

    def __str__(self):
        return self.name


class AdmProducts(models.Model):
    name = models.CharField(max_length=50, unique=True)
    images = models.ImageField(upload_to="product_images/")
    brand = models.CharField(max_length=50, null=True, blank=True)
    category = models.ForeignKey(
        AdmCategories, on_delete=models.CASCADE, related_name="products"
    )
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_type = models.CharField(max_length=50, null=True, blank=True)
    discount_percentage = models.IntegerField()
    description = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )
    is_active = models.BooleanField(default=True)  # New field for soft delete

    def __str__(self):
        return self.name


class VariantImage(models.Model):
    image = models.ImageField(upload_to="variant_images/")
    is_active = models.BooleanField(default=True)  # New field for soft delete


class ProductVariant(models.Model):
    product = models.ForeignKey(AdmProducts, on_delete=models.CASCADE)
    images = models.ManyToManyField(VariantImage, blank=True)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)  # New field for soft delete

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.size.name}"


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    minimum_amount = models.IntegerField()
    discount = models.DecimalField(max_digits=20, decimal_places=2)
    is_expired = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()

    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        now = timezone.now().date()
        return self.valid_from <= now <= self.valid_to
