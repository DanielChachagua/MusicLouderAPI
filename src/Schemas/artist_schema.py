from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional


class ArtistRequest(BaseModel):
    name: str
    bio: Optional[str] = '' or None
    created_by: int

class ArtistDTOResponse(BaseModel):
    id: int
    name: str
    bio: str
    url_image: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# class ArtistResponse(BaseModel):
#     id: int
#     name: str
#     bio: str
#     url_image: str
#     albums: Optional[List[AlbumDTOResponse]]
#     created_by: UserInfo
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

class ArtistPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    artist: List[ArtistDTOResponse]