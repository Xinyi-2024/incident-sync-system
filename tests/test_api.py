import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.severity import classify_severity

client = TestClient(app)


# ── Severity Tests ─────────────────────────────────────────
def test_severity_high():
    assert classify_severity("Production database timeout") == "HIGH"

def test_severity_high_crash():
    assert classify_severity("Server crash in production") == "HIGH"

def test_severity_low():
    assert classify_severity("Fix typo in docs") == "LOW"

def test_severity_medium():
    assert classify_severity("Update user profile endpoint") == "MEDIUM"


# ── API Tests ──────────────────────────────────────────────
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Incident Sync System" in response.json()["service"]

def test_receive_high_incident():
    payload = {
        "source": "github",
        "event_type": "issue_created",
        "title": "Production database timeout",
        "status": "open",
        "assignee": "team-backend"
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "HIGH"
    assert "Alert dispatched" in data["message"]

def test_receive_low_incident():
    payload = {
        "source": "jira",
        "event_type": "issue_created",
        "title": "Fix typo in README docs",
        "status": "open"
    }
    response = client.post("/api/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "LOW"

def test_invalid_payload():
    response = client.post("/api/incidents", json={"bad": "data"})
    assert response.status_code == 422  # Pydantic validation error
