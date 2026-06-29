from typing import Literal
from pydantic import BaseModel


class JiraTicket(BaseModel):
    id: str
    title: str
    resolution: str


class Incident(BaseModel):
    incident_id: str
    alert_name: str
    service_affected: str
    severity: Literal["critical", "high", "medium", "low"]
    timestamp: str
    error_log: str
    slack_thread: list[str]
    jira_ticket: JiraTicket
    git_commits: list[str]
    fix_applied: str
    outcome: Literal["resolved", "rolled-back", "escalated"]
    engineer_name: str
    resolution_time_minutes: int


class RecallRequest(BaseModel):
    alert_text: str


class HealthResponse(BaseModel):
    status: str
