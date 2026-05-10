import requests
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_notification(incident_id: int, title: str, severity: str, source: str):
    """
    Send a Slack notification via webhook.
    In production this is handled by Azure Logic Apps,
    but we also support direct webhook calls here.
    """
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL == "your-slack-webhook-url":
        # No real webhook configured — just log it
        print(f"[SLACK SIMULATED] #{severity} incident #{incident_id}: {title} (from {source})")
        return

    emoji = "🔴" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
    message = {
        "text": f"{emoji} *[{severity}] New Incident #{incident_id}*\n"
                f"*Title:* {title}\n"
                f"*Source:* {source}\n"
                f"*Action required:* {'Immediate response needed!' if severity == 'HIGH' else 'Please review.'}"
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    if response.status_code == 200:
        print(f"Slack notification sent for incident #{incident_id}")
    else:
        print(f"Slack notification failed: {response.status_code}")


def send_escalation_alert(incident_id: int, title: str, minutes_unresolved: int):
    """Send escalation alert for HIGH incidents unresolved too long."""
    print(f"[ESCALATION] Incident #{incident_id} '{title}' unresolved for {minutes_unresolved}+ minutes!")

    if SLACK_WEBHOOK_URL and SLACK_WEBHOOK_URL != "your-slack-webhook-url":
        message = {
            "text": f"🚨 *ESCALATION ALERT*\n"
                    f"Incident #{incident_id} has been unresolved for *{minutes_unresolved}+ minutes*.\n"
                    f"Title: {title}\n"
                    f"Please assign immediately!"
        }
        requests.post(SLACK_WEBHOOK_URL, json=message)
