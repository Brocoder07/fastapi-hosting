import re
from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ChatResponse
from ..database import collection
from ..services.ai_handler import ai_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    try:
        user_query = request.question
        
        # --- 1. VECTOR SEARCH (Semantic Retrieval) ---
        # Good for "vibes" (e.g., Angry -> Liver)
        query_vector = ai_service.get_embedding(user_query)

        vector_pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "patterns.embedding",
                    "queryVector": query_vector,
                    "numCandidates": 50,
                    "limit": 3
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "organ": 1,
                    # Project specific fields to optimize payload
                    "patterns.pattern": 1,
                    "patterns.symptoms": 1,
                    "patterns.treatment_points": 1
                }
            }
        ]
        
        vector_results = await collection.aggregate(vector_pipeline).to_list(3)

        # --- 2. KEYWORD SEARCH (Precision Retrieval) ---
        # Good for specific terms (e.g., "Temple", "Bitter") that Vector might miss
        keywords = [word for word in user_query.split() if len(word) > 3]
        
        keyword_results = []
        if keywords:
            # Create a regex to find ANY significant word from the query
            regex_pattern = "|".join([re.escape(word) for word in keywords])
            keyword_query = {
                "$or": [
                    {"patterns.symptoms": {"$regex": regex_pattern, "$options": "i"}},
                    {"patterns.pattern": {"$regex": regex_pattern, "$options": "i"}}
                ]
            }
            # Fetch top 2 explicit keyword matches
            keyword_results = await collection.find(keyword_query, {"_id": 0}).to_list(2)

        # --- 3. MERGE & DEDUPLICATE ---
        # Combine results from both sources, ensuring Organs aren't repeated
        combined_results = {}
        
        # Add vector results first
        for doc in vector_results:
            combined_results[doc['organ']] = doc
            
        # Add/Overwrite with keyword results (Precision matches are valuable)
        for doc in keyword_results:
            combined_results[doc['organ']] = doc
            
        final_results = list(combined_results.values())
        
        if not final_results:
            return {
                "answer": "I couldn't find any specific protocols in the database matching those symptoms. Please try searching for specific keywords.",
                "related_organs": []
            }

        # --- 4. CONTEXT CONSTRUCTION (Smart Filtering) ---
        # Filter the huge list of patterns to only show the AI what matters
        context_str = ""
        related_organs = []
        
        for doc in final_results:
            organ = doc.get('organ', 'Unknown')
            related_organs.append(organ)
            context_str += f"\n--- ORGAN: {organ} ---\n"
            
            all_patterns = doc.get('patterns', [])
            relevant_patterns = []
            
            # Logic: If a pattern actually contains one of the user's keywords, prioritize it.
            for p in all_patterns:
                # Flatten pattern text for searching
                p_text = (p.get('pattern', '') + " " + " ".join(p.get('symptoms', []))).lower()
                
                # Check for matches
                if any(k.lower() in p_text for k in keywords):
                    relevant_patterns.append(p)
            
            # Fallback: If no keywords matched explicitly, show the top 3 patterns
            # (Use 'relevant_patterns' if it exists, otherwise 'all_patterns[:3]')
            patterns_to_show = relevant_patterns if relevant_patterns else all_patterns[:3]

            for p in patterns_to_show:
                context_str += f"Pattern: {p.get('pattern')}\n"
                context_str += f"Symptoms: {', '.join(p.get('symptoms', []))}\n"
                context_str += f"Points: {', '.join(p.get('treatment_points', []))}\n"

        # --- 5. GENERATE ANSWER ---
        ai_response = ai_service.generate_answer(user_query, context_str)

        return {
            "answer": ai_response,
            "related_organs": list(set(related_organs))
        }

    except Exception as e:
        print(f"AI Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")