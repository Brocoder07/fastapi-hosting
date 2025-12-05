import time
from typing import List
from fastapi import APIRouter, HTTPException
from ..database import bookmarks_collection
from ..models import Bookmark

router = APIRouter()

# 1. Add a Bookmark
@router.post("/users/bookmarks", response_model=dict)
async def add_bookmark(bookmark: Bookmark):
    try:
        # Check if already exists to avoid duplicates
        existing = await bookmarks_collection.find_one({
            "uid": bookmark.uid,
            "organ": bookmark.organ,
            "pattern": bookmark.pattern
        })
        
        if existing:
            return {"message": "Bookmark already exists"}

        # Add timestamp
        bookmark_dict = bookmark.dict()
        bookmark_dict["timestamp"] = time.time()
        
        await bookmarks_collection.insert_one(bookmark_dict)
        return {"message": "Bookmark added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# 2. Get User's Bookmarks
@router.get("/users/{uid}/bookmarks", response_model=List[Bookmark])
async def get_bookmarks(uid: str):
    try:
        # Fetch bookmarks for this specific user, sorted by newest first
        cursor = bookmarks_collection.find({"uid": uid}).sort("timestamp", -1)
        bookmarks = await cursor.to_list(length=100)
        return bookmarks

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# 3. Remove a Bookmark
@router.delete("/users/{uid}/bookmarks")
async def delete_bookmark(uid: str, organ: str, pattern: str):
    try:
        result = await bookmarks_collection.delete_one({
            "uid": uid,
            "organ": organ,
            "pattern": pattern
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Bookmark not found")
            
        return {"message": "Bookmark removed successfully"}

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")