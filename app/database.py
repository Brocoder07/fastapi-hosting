import motor.motor_asyncio
import certifi
from .config import settings

# Initialize Mongo Client with SSL Fix
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI, 
    tlsCAFile=certifi.where()
)

database = client[settings.DB_NAME]
collection = database[settings.COLLECTION_NAME]
bookmarks_collection = database[settings.BOOKMARKS_COLLECTION]
history_collection = database[settings.HISTORY_COLLECTION]