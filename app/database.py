import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully 🚀")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("   Falling back to localhost MongoDB...")
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)

db = client["eduhub"]

# --- Core Collections ---
users_collection = db["users"]
resources_collection = db["resources"]
reviews_collection = db["reviews"]
quotes_collection = db["quotes"]

# --- New Feature Collections ---
scan_logs_collection = db["scan_logs"]
comments_collection = db["comments"]
likes_collection = db["likes"]
reports_collection = db["reports"]
ocr_results_collection = db["ocr_results"]
token_logs_collection = db["token_logs"]
groups_collection = db["groups"]
group_posts_collection = db["group_posts"]

# --- Indexes (idempotent) ---
resources_collection.create_index("file_hash", unique=True, sparse=True)
likes_collection.create_index([("resource_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
token_logs_collection.create_index("user_id")
comments_collection.create_index("resource_id")
reports_collection.create_index("resource_id")
groups_collection.create_index("name", unique=True)
group_posts_collection.create_index("group_id")