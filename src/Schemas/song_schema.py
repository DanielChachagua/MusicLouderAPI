from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List,Optional

from ..Schemas.genre_schema import GenreDTOResponse

class SongRequest(BaseModel):
    title: str
    duration: int
    url_song: str
    album: int
    artist: int
    created_by: str

class SongDTOResponse(BaseModel):
    id: int
    title: str
    duration: int
    url_song: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# class SongResponse(BaseModel):
#     id: int
#     title: str
#     duration: int
#     url_song: str
#     album: Optional[AlbumDTOResponse] = None
#     artist: Optional[ArtistDTOResponse] = None
#     genres: List[GenreDTOResponse]
#     created_by: UserInfo
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

class SongPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    songs: List[SongDTOResponse]