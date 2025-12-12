import os, json, logging
import azure.functions as func
from azure.cosmos import CosmosClient
from datetime import datetime

# Беремо параметри з оточення
COSMOS_URL = os.environ["COSMOS_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB = os.environ.get("COSMOS_DB", "IoTDatabase")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "DeviceData")

# Ініціалізуємо клієнт через URL та ключ
cosmos = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
db = cosmos.get_database_client(COSMOS_DB)

try:
    container = db.get_container_client(COSMOS_CONTAINER)
except Exception:
    # Якщо контейнер ще не створено
    db.create_container(id=COSMOS_CONTAINER, partition_key="/sensorId")
    container = db.get_container_client(COSMOS_CONTAINER)

def main(msg: func.ServiceBusMessage):
    try:
        body = msg.get_body().decode('utf-8')
        data = json.loads(body)
        # Додаємо унікальний id та timestamp
        data.setdefault("id", f"{data.get('sensorId','unknown')}-{int(datetime.utcnow().timestamp()*1000)}")
        data.setdefault("ingestedAt", datetime.utcnow().isoformat() + "Z")
        # Зберігаємо у Cosmos
        container.create_item(body=data)
        logging.info(f"Saved to Cosmos: {data['id']}")
    except Exception as e:
        logging.exception("Processing failed")
        # підкидаємо помилку, щоб Service Bus обробив повтори та DLQ
        raise
