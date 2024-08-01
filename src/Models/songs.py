from pydantic import BaseModel
from datetime import datetime
from typing import List
    
class SongResponse(BaseModel):
    title: str
    duration: int  # Duración en segundos
    album: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    songs: List[SongResponse]