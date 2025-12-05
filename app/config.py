import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    DB_NAME: str = "accupuncture_db"
    COLLECTION_NAME: str = "accupuncture_data"
    BOOKMARKS_COLLECTION: str = "user_bookmarks"
    HISTORY_COLLECTION: str = "chat_history"
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"

settings = Settings()