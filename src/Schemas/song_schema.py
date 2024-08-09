from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List,Optional

class AlbumDTO(BaseModel):
    id: int
    title: str
    url_image: str

    class Config:
        from_attributes = True

class ArtistDTO(BaseModel):
    id: int
    name: str
    url_image: str

    class Config:
        from_attributes = True

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
    album: Optional[AlbumDTO] = None
    artist: Optional[ArtistDTO] = None
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