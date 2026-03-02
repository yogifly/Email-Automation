from dateparser.search import search_dates
from datetime import datetime, timedelta
import re

DEFAULT_HOUR = 9

def extract_event_datetime(subject: str, body: str):
    text = f"{subject} {body}"
    text_lower = text.lower()
    now = datetime.now()

    # -------- 1️⃣ Relative Rules --------

    if "day after tomorrow" in text_lower:
        return (now + timedelta(days=2)).replace(hour=DEFAULT_HOUR, minute=0, second=0)

    if "tomorrow" in text_lower:
        return (now + timedelta(days=1)).replace(hour=DEFAULT_HOUR, minute=0, second=0)

    if "next week" in text_lower:
        days_until_next_monday = (7 - now.weekday())
        next_monday = now + timedelta(days=days_until_next_monday)
        return next_monday.replace(hour=DEFAULT_HOUR, minute=0, second=0)

    # -------- 2️⃣ Extract Full DateTime from Sentence --------

    results = search_dates(
        text,
        settings={
            "PREFER_DATES_FROM": "future",
            "RETURN_AS_TIMEZONE_AWARE": False,
        }
    )

    if not results:
        return None

    # Choose the most complete datetime match
    best_match = None

    for match_text, dt in results:

        # Skip unrealistic past dates
        if dt < now:
            continue

        # Prefer matches containing both date and time
        has_time = bool(re.search(r"\d{1,2}(:\d{2})?\s?(am|pm)", match_text.lower()))
        has_date = bool(re.search(r"\d{1,2}", match_text))

        if has_date and has_time:
            best_match = dt
            break

        if not best_match:
            best_match = dt

    if not best_match:
        return None

    # If no time mentioned, assign default hour
    if best_match.hour == 0 and best_match.minute == 0:
        best_match = best_match.replace(hour=DEFAULT_HOUR)

    return best_match