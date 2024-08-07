from pydantic import BaseModel
from datetime import datetime
from typing import List
from ..Schemas.user_schema import UserInfo

class PlayListRequest(BaseModel):
    name: str
    songs: List[int]
    created_by: int

class PlayListDTOResponse(BaseModel):
    id: int
    name: str
    created_by: UserInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# class PlayListResponse(BaseModel):
#     id: int
#     title: str
#     songs: List[SongResponse]
#     created_by: int
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True