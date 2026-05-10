import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/incidents")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id          SERIAL PRIMARY KEY,
            source      VARCHAR(50),
            event_type  VARCHAR(50),
            title       TEXT,
            severity    VARCHAR(10),
            status      VARCHAR(20),
            assignee    VARCHAR(100),
            description TEXT,
            created_at  TIMESTAMP DEFAULT NOW(),
            updated_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id           SERIAL PRIMARY KEY,
            incident_id  INT REFERENCES incidents(id),
            action       TEXT,
            performed_by VARCHAR(100) DEFAULT 'system',
            performed_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")


def save_incident(event: dict, severity: str) -> int:
    """Save a new incident and return its ID."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO incidents (source, event_type, title, severity, status, assignee, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, created_at;
    """, (
        event["source"],
        event["event_type"],
        event["title"],
        severity,
        event["status"],
        event.get("assignee"),
        event.get("description"),
    ))

    row = cur.fetchone()
    incident_id, created_at = row[0], row[1]

    # Write to audit log
    cur.execute("""
        INSERT INTO audit_log (incident_id, action)
        VALUES (%s, %s);
    """, (incident_id, f"Incident created with severity {severity}"))

    conn.commit()
    cur.close()
    conn.close()

    return incident_id, created_at


def get_unresolved_high_incidents(older_than_minutes: int = 60):
    """Find HIGH severity incidents unresolved for longer than given minutes."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, created_at
        FROM incidents
        WHERE severity = 'HIGH'
          AND status != 'closed'
          AND created_at < NOW() - INTERVAL '%s minutes';
    """, (older_than_minutes,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
