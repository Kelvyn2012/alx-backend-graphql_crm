from datetime import datetime
import requests
from celery import shared_task
import json

@shared_task
def generate_crm_report():
    # Example GraphQL query
    query = """
    {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    """

    response = requests.post(
        "http://localhost:8000/graphql/",
        json={"query": query},
        headers={"Content-Type": "application/json"},
    )

    data = response.json()
    customers = data.get("data", {}).get("allCustomers", {}).get("totalCount", 0)
    orders = data.get("data", {}).get("allOrders", {}).get("totalCount", 0)
    revenue = sum(
        edge["node"]["totalAmount"] for edge in data.get("data", {}).get("allOrders", {}).get("edges", [])
    )

    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(log_entry)
