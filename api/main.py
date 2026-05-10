from fastapi import FastAPI
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from api.models import IncidentEvent, IncidentResponse
from api.severity import classify_severity
from api.notifications import send_slack_notification

try:
    from api.database import init_db, save_incident
    USE_DB = True
except Exception:
    USE_DB = False

mock_store = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    if USE_DB:
        try:
            init_db()
        except Exception:
            pass
    yield


app = FastAPI(
    title="Incident Sync System",
    description="Cloud-native incident synchronization and auto-dispatch API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "service": "Incident Sync System",
        "status": "running",
        "version": "1.0.0",
        "endpoints": ["/api/incidents", "/api/incidents/list", "/health"]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/incidents", response_model=IncidentResponse)
def receive_incident(event: IncidentEvent):
    """
    Main webhook endpoint.
    Receives an incident event, classifies severity,
    saves to DB (or mock store), and dispatches notifications.
    """
    severity = classify_severity(event.title, event.description or "")

    incident_id = None
    created_at = None

    if USE_DB:
        try:
            incident_id, created_at = save_incident(event.model_dump(), severity)
        except Exception:
            pass

    if incident_id is None:
        incident_id = len(mock_store) + 1
        created_at = datetime.now(timezone.utc)
        mock_store.append({
            "id": incident_id,
            "severity": severity,
            "title": event.title,
            "source": event.source,
            "status": event.status,
            "created_at": created_at
        })

    if severity == "HIGH":
        send_slack_notification(incident_id, event.title, severity, event.source)

    return IncidentResponse(
        id=incident_id,
        source=event.source,
        title=event.title,
        severity=severity,
        status=event.status,
        message=f"Incident #{incident_id} received. Severity: {severity}. "
                + ("Alert dispatched!" if severity == "HIGH" else "Queued for review."),
        created_at=created_at
    )


@app.get("/api/incidents/list")
def list_incidents():
    return {"incidents": mock_store, "total": len(mock_store)}
