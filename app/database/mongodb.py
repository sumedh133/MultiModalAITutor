from pymongo import MongoClient
from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)

db = client["agriassist"]

users_collection = db["users"]
chat_collection = db["chats"]
profile_collection = db["profiles"]