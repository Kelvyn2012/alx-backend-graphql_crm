from datetime import datetime
import requests

def log_crm_heartbeat():
    """Logs a heartbeat message to confirm the CRM app is running."""
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    log_path = "/tmp/crm_heartbeat_log.txt"

    # Write heartbeat message
    with open(log_path, "a") as log_file:
        log_file.write(message)

    # Optional: verify GraphQL endpoint health
    try:
        response = requests.post(
            "http://localhost:8000/graphql/",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            with open(log_path, "a") as log_file:
                log_file.write(f"{timestamp} GraphQL OK\n")
        else:
            with open(log_path, "a") as log_file:
                log_file.write(f"{timestamp} GraphQL check failed ({response.status_code})\n")
    except Exception as e:
        with open(log_path, "a") as log_file:
            log_file.write(f"{timestamp} GraphQL check error: {str(e)}\n")
