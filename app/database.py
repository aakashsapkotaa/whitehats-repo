import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["eduhub"]

users_collection = db["users"]
resources_collection = db["resources"]
reviews_collection = db["reviews"]
quotes_collection = db["quotes"]

print("MongoDB Connected Successfully 🚀")