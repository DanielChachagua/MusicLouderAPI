from pydantic import BaseModel
from datetime import datetime
from typing import List
from ..Models.user import UserInfo
from ..Models.albums import AlbumResponse
from ..Models.artists import ArtistResponse

class GenreRequest(BaseModel):
    name: str

    
class GenreResponse(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
