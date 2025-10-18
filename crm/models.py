from django.db import models
from django.utils import timezone


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(Product, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Save the order first to ensure it has an ID
        super().save(*args, **kwargs)

        # Calculate the total amount from related products
        total = sum(p.price for p in self.products.all())

        # Update only if total has changed to avoid infinite recursion
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"
