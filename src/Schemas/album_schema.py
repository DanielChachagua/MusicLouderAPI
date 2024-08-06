from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class AlbumRequest(BaseModel):
    title: str
    artist: Optional[int] = None
    release_date: date
    created_by: int

class AlbumDTOResponse(BaseModel):
    id: int
    title: str
    release_date: date
    url_image: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True    

# class AlbumResponse(BaseModel):
#     title: str
#     artist: Optional[ArtistDTOResponse] = None
#     songs: Optional[List[SongDTOResponse]]
#     release_date: date
#     url_image: str
#     created_by: UserInfo
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

class AlbumPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    albums: List[AlbumDTOResponse]