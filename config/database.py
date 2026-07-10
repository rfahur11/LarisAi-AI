from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import get_settings

settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    
    @classmethod
    def get_db(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        return cls.client[settings.MONGODB_DB_NAME]
        
    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            cls.client = None

db = Database()
