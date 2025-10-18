from crm.models import Customer, Product, Order
from django.utils import timezone

# Clear existing data (optional)
Order.objects.all().delete()
Customer.objects.all().delete()
Product.objects.all().delete()

# Create some customers
customers = [
    Customer(name="Alice Johnson", email="alice@example.com", phone="+1234567890"),
    Customer(name="Bob Smith", email="bob@example.com", phone="123-456-7890"),
    Customer(name="Carol White", email="carol@example.com"),
]
Customer.objects.bulk_create(customers)

# Create some products
products = [
    Product(name="Laptop", price=999.99, stock=10),
    Product(name="Phone", price=499.99, stock=25),
    Product(name="Headphones", price=89.99, stock=50),
]
Product.objects.bulk_create(products)

# Fetch instances again (bulk_create doesn’t return IDs)
alice = Customer.objects.get(email="alice@example.com")
laptop = Product.objects.get(name="Laptop")
phone = Product.objects.get(name="Phone")

# ✅ Correct way: Save the order first, then set products, then compute total
order = Order.objects.create(customer=alice, order_date=timezone.now())
order.products.set([laptop, phone])
order.total_amount = sum(p.price for p in order.products.all())
order.save()

print("✅ Database seeded successfully!")
print(f"Customers: {Customer.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
