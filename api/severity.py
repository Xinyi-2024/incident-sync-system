def classify_severity(title: str, description: str = "") -> str:
    """
    Classify incident severity based on keywords in title and description.
    Returns: "HIGH", "MEDIUM", or "LOW"
    """
    text = (title + " " + (description or "")).lower()

    high_keywords = [
        "timeout", "crash", "down", "critical", "production",
        "outage", "failure", "emergency", "urgent", "broken"
    ]
    low_keywords = [
        "docs", "typo", "minor", "cosmetic", "enhancement",
        "question", "feature request", "nice to have"
    ]

    if any(keyword in text for keyword in high_keywords):
        return "HIGH"
    elif any(keyword in text for keyword in low_keywords):
        return "LOW"
    else:
        return "MEDIUM"
