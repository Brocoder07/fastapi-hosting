from typing import List
from pydantic import BaseModel

# --- Domain Models ---
class PatternData(BaseModel):
    pattern: str
    symptoms: List[str]
    treatment_points: List[str]

class AcupunctureData(BaseModel):
    organ: str
    patterns: List[PatternData]

# --- API Request/Response Models ---
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    related_organs: List[str]

class OrganStat(BaseModel):
    organ: str
    pattern_count: int

class Bookmark(BaseModel):
    uid: str
    Organ: str
    Pattern: str
    timestamp: float = None

class ChatLog(BaseModel):
    uid: str
    question: str
    answer: str
    related_organs: List[str]
    timestamp: float = None