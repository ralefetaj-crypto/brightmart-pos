from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Supplier(models.Model):
name = models.CharField(max_length=150)
contact_person = models.CharField(max_length=100, blank=True)
phone = models.CharField(max_length=30, blank=True)
email = models.EmailField(blank=True)

def __str__ (self):
                    return self.name


class Product(models.Model):

CATEGORY_CHOICES = [
("HOUSEHOLD", "Household Goods"),
("STATIONERY", "Stationery"),
("CONVENIENCE", "Convenience Products"),
 ]

name = models.CharField(max_length=150)
category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="CONVENIENCE")
supplier = models.ForeignKey(
Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
)
price = models.DecimalField(max_digits=10, decimal_places=2)
quantity = models.PositiveIntegerField(default=0)
reorder_level = models.PositiveIntegerField(default=10)


@property
def is_low_stock(self):
return self.quantity <= self.reorder_level

def str(self):
return f"{self.name} ({self.quantity} in stock)"


class Sale(models.Model):
product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales")
quantity_sold = models.PositiveIntegerField()
unit_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
total_amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

sold_at = models.DateTimeField(default=timezone.now)

def clean(self):
if self.quantity_sold is not None and self.quantity_sold < 1:
raise ValidationError("Quantity sold must be at least 1.")
if self.pk is None and self.product_id and self.quantity_sold:
if self.quantity_sold > self.product.quantity:
raise ValidationError(
f"Insufficient stock for {self.product.name}. Available: {self.product.quantity}."
)

def save(self, *args, **kwargs):
is_new = self.pk is None
with transaction.atomic():
if is_new:

product = Product.objects.select_for_update().get(pk=self.product.pk)
if self.quantity_sold > product.quantity:
raise ValidationError(
f"Insufficient stock for {product.name}. Available: {product.quantity}."
)
self.unit_price = product.price
self.total_amount = Decimal(self.quantity_sold) * product.price
product.quantity -= self.quantity_sold
product.save(update_fields=["quantity"])
self.product = product
super().save(*args, **kwargs)

def str(self):
return f"Sale #{self.pk}: {self.quantity_sold} x {self.product.name}"