from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Log to /tmp
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optional GraphQL check
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("{ hello }")
        result = client.execute(query)
        print("GraphQL hello check:", result)
    except Exception as e:
        print("GraphQL check failed:", e)
def update_low_stock():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    updatedProducts {
                        name
                        stock
                    }
                }
            }
        """)
        result = client.execute(mutation)
        updates = result["updateLowStockProducts"]["updatedProducts"]
        success_msg = result["updateLowStockProducts"]["success"]

        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - {success_msg}\n")
            for p in updates:
                f.write(f"    {p['name']}: new stock {p['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - Error: {str(e)}\n")