import logging
import azure.functions as func

def main(msg: func.ServiceBusMessage):
    try:
        body = msg.get_body().decode('utf-8')
        logging.warning(f"Message in DLQ: {body}")
        # here you can implement reprocessing, alerting, saving to blob, etc.
    except Exception:
        logging.exception("DLQ handler error")
