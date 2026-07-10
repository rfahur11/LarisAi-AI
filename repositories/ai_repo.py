from typing import List, Dict, Any
from config.database import Database

class AIRepository:
    
    @staticmethod
    async def get_active_products() -> List[Dict[str, Any]]:
        db = Database.get_db()
        cursor = db["products"].find({"is_archived": False})
        return await cursor.to_list(length=None)
        
    @staticmethod
    async def get_active_customers() -> List[Dict[str, Any]]:
        db = Database.get_db()
        cursor = db["customers"].find({"is_archived": False})
        return await cursor.to_list(length=None)
        
    @staticmethod
    async def get_valid_transactions() -> List[Dict[str, Any]]:
        db = Database.get_db()
        cursor = db["transactions"].find({"is_archived": False})
        return await cursor.to_list(length=None)
