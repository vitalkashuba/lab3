import azure.functions as func
import os, json, logging
from azure.cosmos import CosmosClient

COSMOS_CONN = os.environ["COSMOS_CONN"]
COSMOS_DB = os.environ.get("COSMOS_DB", "IoTDatabase")
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "DeviceData")

cosmos = CosmosClient.from_connection_string(COSMOS_CONN)
db = cosmos.get_database_client(COSMOS_DB)
container = db.get_container_client(COSMOS_CONTAINER)

def main(req: func.HttpRequest) -> func.HttpResponse:
    sensor_id = req.params.get("sensorId")
    sensor_type = req.params.get("sensorType")
    limit = req.params.get("limit")
    try:
        limit = int(limit) if limit else 100
        params = []
        where = []
        if sensor_id:
            where.append("c.sensorId = @sensorId")
            params.append({"name": "@sensorId", "value": sensor_id})
        if sensor_type:
            where.append("c.sensorType = @sensorType")
            params.append({"name": "@sensorType", "value": sensor_type})

        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        query = f"SELECT TOP {limit} * FROM c {where_clause} ORDER BY c.ingestedAt DESC"

        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        result = {"success": True, "count": len(items), "data": items}
        return func.HttpResponse(json.dumps(result, default=str), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.exception("Query failed")
        return func.HttpResponse(json.dumps({"success": False, "error": str(e)}), mimetype="application/json", status_code=500)
