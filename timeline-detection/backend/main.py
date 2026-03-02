from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from database import events_collection
from email_parser import extract_event_datetime
from scheduler import start_scheduler
from datetime import datetime
import asyncio

app = FastAPI()

# Allow Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def broadcast(self, message):
        for connection in self.active_connections:
            asyncio.create_task(connection.send_text(message))

manager = ConnectionManager()
start_scheduler(manager)

@app.post("/create-event/")
def create_event(subject: str, body: str):

    print("Received:", subject, body)

    event_time = extract_event_datetime(subject, body)

    print("Parsed datetime:", event_time)

    if not event_time:
        return {"message": "No date detected"}

    event_doc = {
        "title": subject,
        "description": body,
        "event_time": event_time
    }

    result = events_collection.insert_one(event_doc)

    print("Inserted ID:", result.inserted_id)

    return {
        "message": "Event saved",
        "time": event_time.isoformat()
    }

@app.get("/events/")
def get_events():

    events = []

    for event in events_collection.find():
        events.append({
            "title": event["title"],
            "description": event["description"],
            "event_time": event["event_time"].isoformat()
        })

    return events

from fastapi import WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("Client disconnected normally")