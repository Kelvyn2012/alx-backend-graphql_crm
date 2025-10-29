import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    try:
        # GraphQL setup
        transport = RequestsHTTPTransport(
            url='http://localhost:8000/graphql/',
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""
        query {
            allCustomers { totalCount }
            allOrders { totalCount }
            totalRevenue
        }
        """)

        response = client.execute(query)
        customers = response.get('allCustomers', {}).get('totalCount', 0)
        orders = response.get('allOrders', {}).get('totalCount', 0)
        revenue = response.get('totalRevenue', 0)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_line)

    except Exception as e:
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(f"Error generating report: {e}\n")
