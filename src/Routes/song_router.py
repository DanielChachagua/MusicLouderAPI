from fastapi import APIRouter, HTTPException, Query
from ..Models.songs import *
from ..Database.db import *
from typing import List
import math

song_router = APIRouter()

@song_router.get('/', response_model=PaginatedResponse)
async def get_songs(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> PaginatedResponse:
    try:
        offset = (page - 1) * size
        limit = size
        total_count = Song.select().count()
        users_query = Song.select().limit(limit).offset(offset)
        song_list = [SongResponse.model_validate(song) for song in users_query]
        total_pages = math.ceil(total_count / size)
        return {
            "page": page,
            "size": size,
            "total_count": total_count,
            "total_pages": total_pages,
            "songs": song_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 