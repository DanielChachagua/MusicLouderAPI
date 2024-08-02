from pydantic import BaseModel
from datetime import datetime
from typing import List,Optional
from ..Models.user import UserInfo
from ..Models.albums import AlbumResponse
from ..Models.artists import ArtistResponse
from ..Models.genres import GenreResponse

class SongRequest(BaseModel):
    title: str
    duration: int
    url_song: str
    album: int
    artist: int
    created_by: str

    
class SongResponse(BaseModel):
    title: str
    duration: int
    url_song: str
    album: Optional[AlbumResponse] = None
    artist: Optional[ArtistResponse] = None
    genres: List[GenreResponse]
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SongPaginatedResponse(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int
    songs: List[SongResponse]