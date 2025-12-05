import time
from typing import List
from fastapi import APIRouter, HTTPException, Query
from ..database import history_collection
from ..models import ChatLog

router = APIRouter()

# 1. Save a Chat Interaction
# Call this from Android immediately after the AI responds
@router.post("/chat/history", response_model=dict)
async def save_chat_log(log: ChatLog):
    try:
        log_dict = log.dict()
        log_dict["timestamp"] = time.time()
        
        await history_collection.insert_one(log_dict)
        return {"message": "Chat saved successfully"}

    except Exception as e:
        # Don't crash the app if history save fails, just log it
        print(f"History Save Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save history")

# 2. Get User's Chat History (Paginated)
@router.get("/chat/history/{uid}", response_model=List[ChatLog])
async def get_chat_history(
    uid: str, 
    limit: int = Query(20, le=50), # Default 20, max 50 per page
    skip: int = 0
):
    try:
        # Sort by newest first (descending timestamp)
        cursor = history_collection.find({"uid": uid})\
            .sort("timestamp", -1)\
            .skip(skip)\
            .limit(limit)
            
        history = await cursor.to_list(length=limit)
        return history

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# 3. Clear History (Privacy feature)
@router.delete("/chat/history/{uid}")
async def clear_chat_history(uid: str):
    try:
        result = await history_collection.delete_many({"uid": uid})
        return {"message": f"Deleted {result.deleted_count} chat records"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")