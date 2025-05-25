from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGODB_URL = config("MONGODB_URL")
DATABASE_NAME = config("DATABASE_NAME")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

users_collection = database["users"]
conversations_collection = database["conversations"]

async def close_db_connection():
    client.close()