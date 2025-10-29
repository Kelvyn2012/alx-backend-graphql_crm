from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from crm.models import Product
from django.utils import timezone
from django.db import transaction
import re



# ===== Object Types =====
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


# ===== Input Types =====
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# ===== Create Customer =====
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        if input.phone and not re.match(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$", input.phone):
            raise Exception("Invalid phone format")

        customer = Customer.objects.create(
            name=input.name, email=input.email, phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully")


# ===== Bulk Create Customers =====
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email already exists: {data.email}")
                    continue
                if data.phone and not re.match(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$", data.phone):
                    errors.append(f"Invalid phone format: {data.phone}")
                    continue
                customer = Customer.objects.create(
                    name=data.name, email=data.email, phone=data.phone
                )
                customers.append(customer)
            except Exception as e:
                errors.append(str(e))
        return BulkCreateCustomers(customers=customers, errors=errors)


# ===== Create Product =====
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name, price=input.price, stock=input.stock
        )
        return CreateProduct(product=product, message="Product created successfully")


# ===== Create Order =====
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product ID is required")

        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            raise Exception("One or more product IDs are invalid")

        order = Order.objects.create(
            customer=customer,
            order_date=input.order_date or timezone.now(),
        )
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()

        return CreateOrder(order=order, message="Order created successfully")
    
# ===== Update Low Stock Products =====
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    success = graphene.String()
    updated_products = graphene.List(lambda: ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10  # Simulate restocking
            product.save()
            updated_products.append(product)

        success_msg = f"Updated {len(updated_products)} low-stock products."

        return UpdateLowStockProducts(
            success=success_msg,
            updated_products=updated_products
        )



# ===== Root Mutation =====
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field() 

    



# ===== Query =====
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.String())

    def resolve_all_customers(root, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(root, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(root, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get("order_by")
        if order_by:
            qs = qs.order_by(order_by)
        return qs


    #all_customers = graphene.List(CustomerType)
    #all_products = graphene.List(ProductType)
    #all_orders = graphene.List(OrderType)

    #def resolve_all_customers(root, info):
        #return Customer.objects.all()

    #def resolve_all_products(root, info):
        #return Product.objects.all()

    #def resolve_all_orders(root, info):
        #return Order.objects.all()