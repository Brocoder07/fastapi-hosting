import re
from typing import List
from fastapi import APIRouter, Query, HTTPException
from ..database import collection
from ..models import AcupunctureData

router = APIRouter()

def validate_query(query: str):
    if not re.match(r'^[a-zA-Z0-9 ]*$', query):
        raise HTTPException(status_code=400, detail="Invalid search term.")

@router.get("/search", response_model=List[AcupunctureData])
async def search_data(query: str = Query(..., min_length=2)):
    validate_query(query)
    try:
        # 1. Exact Organ Match
        organ_query = {"organ": {"$regex": f"^{query}$", "$options": "i"}}
        organ_result = await collection.find_one(organ_query, {"_id": 0})

        if organ_result:
            return [organ_result]

        # 2. Pattern/Symptom Match (Aggregation Pipeline)
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"patterns.pattern": {"$regex": query, "$options": "i"}},
                        {"patterns.symptoms": {"$regex": query, "$options": "i"}}
                    ]
                }
            },
            {"$unwind": "$patterns"},
            {
                "$match": {
                    "$or": [
                        {"patterns.pattern": {"$regex": query, "$options": "i"}},
                        {"patterns.symptoms": {"$regex": query, "$options": "i"}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "organ": {"$first": "$organ"},
                    "patterns": {"$push": "$patterns"}
                }
            },
            {"$project": {"_id": 0}},
            {"$limit": 100}
        ]

        results = await collection.aggregate(pipeline).to_list(100)

        if not results:
            raise HTTPException(status_code=404, detail="No matching data found.")

        return results

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.head("/search")
async def search_head(query: str = Query(..., min_length=2)):
    validate_query(query)
    try:
        organ_query = {"organ": {"$regex": f"^{query}$", "$options": "i"}}
        if await collection.count_documents(organ_query, limit=1) > 0:
            return {"detail": "Resource available"}

        search_query = {
            "$or": [
                {"patterns.pattern": {"$regex": query, "$options": "i"}},
                {"patterns.symptoms": {"$regex": query, "$options": "i"}}
            ]
        }
        if await collection.count_documents(search_query, limit=1) > 0:
            return {"detail": "Resource available"}

        raise HTTPException(status_code=404, detail="No matching data found.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")