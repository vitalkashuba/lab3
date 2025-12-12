import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger for ProcessSensorData received.')

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )

    # Тут можна викликати твою основну логіку обробки сенсорних даних
    # Наприклад, викликати функцію, яка працює з CosmosDB або чергою
    # process_sensor_data(data) <- твоя логіка

    logging.info(f"Received data: {data}")

    return func.HttpResponse(
        json.dumps({"status": "success", "data": data}),
        mimetype="application/json",
        status_code=200
    )
