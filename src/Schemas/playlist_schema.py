from pydantic import BaseModel
from datetime import datetime
from typing import List

class PlayListRequest(BaseModel):
    title: str
    songs: List[int]
    created_by: int

class PlayListDTOResponse(BaseModel):
    id: int
    title: str
    created_by: int
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