import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    # Quick ping to verify
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully 🚀")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("   Falling back to localhost MongoDB...")
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)

db = client["eduhub"]

users_collection = db["users"]
resources_collection = db["resources"]
reviews_collection = db["reviews"]
quotes_collection = db["quotes"]