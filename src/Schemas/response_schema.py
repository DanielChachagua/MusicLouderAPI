from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from .album_schema import AlbumDTOResponse
from .artist_schema import ArtistDTOResponse
from .genre_schema import GenreDTOResponse
from .song_schema import SongDTOResponse
from .user_schema import UserInfo


class AlbumResponse(BaseModel):
    id:int
    title: str
    artist: Optional[ArtistDTOResponse] = None
    songs: Optional[List[SongDTOResponse]]
    release_date: date
    url_image: str
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ArtistResponse(BaseModel):
    id: int
    name: str
    bio: str
    url_image: str
    albums: Optional[List[AlbumDTOResponse]]
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GenreResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlayListResponse(BaseModel):
    id: int
    name: str
    songs: List[SongDTOResponse]
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SongResponse(BaseModel):
    id: int
    title: str
    duration: int
    url_song: str
    album: Optional[AlbumDTOResponse] = None
    artist: Optional[ArtistDTOResponse] = None
    genres: List[GenreDTOResponse]
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True