from typing import List
from fastapi import APIRouter, HTTPException
from ..database import collection
from ..models import OrganStat

router = APIRouter()

@router.get("/metadata/organs", response_model=List[OrganStat])
async def get_organ_stats():
    try:
        pipeline = [
            # 1. Group by Organ name
            {
                "$group": {
                    "_id": "$organ", 
                    "pattern_count": {"$sum": {"$size": "$patterns"}}
                }
            },
            # 2. Rename _id to organ for the Pydantic model
            {
                "$project": {
                    "_id": 0,
                    "organ": "$_id",
                    "pattern_count": 1
                }
            },
            # 3. Sort alphabetically
            {"$sort": {"organ": 1}}
        ]
        
        results = await collection.aggregate(pipeline).to_list(None)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")