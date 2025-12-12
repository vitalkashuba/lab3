import azure.functions as func
import os
import json
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Підключення до Service Bus через environment variables
SB_CONN_STR = os.environ.get("SERVICE_BUS_CONNECTION_STRING")
QUEUE_NAME = os.environ.get("SERVICE_BUS_QUEUE", "iot-sensor-queue")

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP trigger received a request")

    # Перевіряємо JSON
    try:
        payload = req.get_json()
    except ValueError:
        logging.warning("Invalid JSON received")
        return func.HttpResponse("Invalid JSON", status_code=400)

    # Встановлюємо дефолтні значення, якщо їх немає
    payload.setdefault("sensorId", "unknown")
    payload.setdefault("sensorType", "unknown")
    payload.setdefault("value", None)
    payload.setdefault("unit", "")
    payload.setdefault("location", {"lat": 0.0, "lon": 0.0})
    payload.setdefault("timestamp", None)

    # Надсилаємо повідомлення в Service Bus
    try:
        with ServiceBusClient.from_connection_string(SB_CONN_STR) as client:
            with client.get_queue_sender(QUEUE_NAME) as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(payload)))
        logging.info(f"Message sent to queue: {QUEUE_NAME}")
        return func.HttpResponse("Enqueued", status_code=200)
    except Exception as e:
        logging.exception("Failed to send to Service Bus")
        return func.HttpResponse(f"Send failed: {e}", status_code=500)
