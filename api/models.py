from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IncidentEvent(BaseModel):
    source: str                        # e.g. "github", "jira", "crm"
    event_type: str                    # e.g. "issue_updated", "issue_created"
    title: str
    status: str                        # e.g. "open", "closed", "in_progress"
    assignee: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None


class IncidentResponse(BaseModel):
    id: int
    source: str
    title: str
    severity: str
    status: str
    message: str
    created_at: datetime
