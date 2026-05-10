import azure.functions as func
import json
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from api.severity import classify_severity
from api.notifications import send_slack_notification

app = func.FunctionApp()


@app.function_name(name="IncidentReceiver")
@app.route(route="incidents", methods=["POST"])
def incident_receiver(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger.
    Same logic as FastAPI endpoint but runs serverless on Azure.
    """
    logging.info("Incident received via Azure Function.")

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    title = payload.get("title", "")
    source = payload.get("source", "unknown")
    status = payload.get("status", "open")

    severity = classify_severity(title, payload.get("description", ""))

    if severity == "HIGH":
        send_slack_notification(0, title, severity, source)

    response = {
        "status": "received",
        "severity": severity,
        "title": title,
        "source": source,
        "message": f"Severity {severity} — {'Alert dispatched!' if severity == 'HIGH' else 'Queued for review.'}"
    }

    return func.HttpResponse(
        json.dumps(response),
        mimetype="application/json",
        status_code=200
    )
