from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from ..Models.user import UserInfo

class AlbumRequest(BaseModel):
    title: str
    artist: Optional[int] = None
    release_date: date
    url_image: str
    created_by: int

    
class AlbumResponse(BaseModel):
    title: str
    artist: Optional[int] = None
    release_date: date
    url_image: str
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlbumPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    songs: List[AlbumResponse]