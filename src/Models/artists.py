from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
from ..Models.user import UserInfo

class ArtistRequest(BaseModel):
    name: str
    bio: Optional[str] = None
    url_image: str
    created_by: UserInfo

    
class ArtistResponse(BaseModel):
    name: str
    bio: str
    url_image: str
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime = lambda: datetime.now(timezone.utc)

    class Config:
        from_attributes = True

class ArtistPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    songs: List[ArtistResponse]