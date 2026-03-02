from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from database import events_collection
import asyncio

scheduler = BackgroundScheduler()
scheduler.start()

def check_deadlines(manager):
    now = datetime.now()

    events = list(events_collection.find())

    for event in events:
        event_time = event["event_time"]
        seconds_left = (event_time - now).total_seconds()

        # Notify if deadline within next 60 seconds
        if 0 <= seconds_left <= 60:
            manager.broadcast(f"⏰ Deadline reached: {event['title']}")

def start_scheduler(manager):
    scheduler.add_job(lambda: check_deadlines(manager),
                      "interval",
                      seconds=30)