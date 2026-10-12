from typing import List, Dict, Any, Optional
from config.database import Database

class AIRepository:
    
    @staticmethod
    async def get_active_products(store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = Database.get_db()
        query: Dict[str, Any] = {"is_archived": False}
        if store_id:
            query["store_id"] = store_id
        cursor = db["products"].find(query)
        return await cursor.to_list(length=None)
        
    @staticmethod
    async def get_active_customers(store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = Database.get_db()
        query: Dict[str, Any] = {"is_archived": False}
        if store_id:
            query["store_id"] = store_id
        cursor = db["customers"].find(query)
        return await cursor.to_list(length=None)
        
    @staticmethod
    async def get_valid_transactions(store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db = Database.get_db()
        query: Dict[str, Any] = {"is_archived": False}
        if store_id:
            query["store_id"] = store_id
        cursor = db["transactions"].find(query)
        return await cursor.to_list(length=None)
