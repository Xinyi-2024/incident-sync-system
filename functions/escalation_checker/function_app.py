import azure.functions as func
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from api.notifications import send_escalation_alert

app = func.FunctionApp()


@app.function_name(name="EscalationChecker")
@app.timer_trigger(schedule="0 */30 * * * *")  # runs every 30 minutes
def escalation_checker(mytimer: func.TimerRequest) -> None:
    """
    Azure Function Timer trigger.
    Checks every 30 minutes for HIGH incidents unresolved > 60 minutes.
    If found, sends escalation alert.
    """
    logging.info("Escalation checker running...")

    try:
        from api.database import get_unresolved_high_incidents
        unresolved = get_unresolved_high_incidents(older_than_minutes=60)

        if not unresolved:
            logging.info("No unresolved HIGH incidents. All good!")
            return

        for incident_id, title, created_at in unresolved:
            logging.warning(f"Escalating incident #{incident_id}: {title}")
            send_escalation_alert(incident_id, title, minutes_unresolved=60)

    except Exception as e:
        logging.error(f"Escalation checker error: {e}")
