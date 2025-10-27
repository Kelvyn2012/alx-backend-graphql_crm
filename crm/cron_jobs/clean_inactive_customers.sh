#!/bin/bash

PROJECT_DIR="/Users/kelvyn/Documents/Backend/alx_backend_graphql"

cd "$PROJECT_DIR" || exit

# source venv/bin/activate  # uncomment if you use a virtualenv

deleted_count=$(python3 manage.py shell --quiet -c "
from django.utils import timezone
from crm.models import Customer
cutoff = timezone.now() - timezone.timedelta(days=365)
inactive_customers = Customer.objects.exclude(orders__order_date__gte=cutoff)
deleted, _ = inactive_customers.delete()
print(deleted)
")



echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $deleted_count" >> /tmp/customer_cleanup_log.txt
