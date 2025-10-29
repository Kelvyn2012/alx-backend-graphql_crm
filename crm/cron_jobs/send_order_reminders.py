#!/usr/bin/env python3
import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/order_reminders_log.txt"

def log_message(message):
    """Append a message to the log file with a timestamp."""
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"{timestamp} - {message}\n")

def main():
    # Set up the GraphQL transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Build GraphQL query
    query = gql("""
    query {
        orders {
            id
            orderDate
            customer {
                email
            }
        }
    }
    """)

    try:
        result = client.execute(query)
        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)

        for order in result.get("orders", []):
            order_date = datetime.datetime.fromisoformat(order["orderDate"])
            if one_week_ago <= order_date <= now:
                customer_email = order["customer"]["email"]
                log_message(f"Order ID: {order['id']} - Email: {customer_email}")

        print("Order reminders processed!")

    except Exception as e:
        log_message(f"Error processing order reminders: {str(e)}")

if __name__ == "__main__":
    main()
