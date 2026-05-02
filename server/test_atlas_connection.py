# test_atlas_connection.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    mongo_uri = os.getenv("MONGO_URI")
    print(f"Testing connection to: {mongo_uri.split('@')[1]}")  # Print without password
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client.bharatmail
    
    try:
        # Ping the database
        result = await db.command("ping")
        print("✅ Successfully connected to MongoDB Atlas!")
        print(f"Response: {result}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        client.close()

asyncio.run(test_connection())