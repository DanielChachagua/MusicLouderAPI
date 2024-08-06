from typing import List
from fastapi import APIRouter, Query, UploadFile, File, Form, Request
from fastapi.responses import FileResponse

from ..Schemas.response_schema import SongResponse
from ..Schemas.song_schema import SongPaginatedResponse
from ..Services.song_service import SongService

song_router = APIRouter()
# Crear instancia del servicio
song_service = SongService(path_song='src/Multimedia/Music')

@song_router.get('/', response_model=SongPaginatedResponse)
async def get_songs(request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> SongPaginatedResponse:
    return song_service.get_songs(request, page, size)

@song_router.get('/{id}', response_model=SongResponse)
async def get_song(request: Request, id: int):
    return song_service.get_song(request, id)

@song_router.post('/create')
async def create_song(request: Request,
    title: str = Form(...),
    song: UploadFile = File(...),
    created_by: int = Form(...),
    genres: List[str] = Form(...),
):
    content = await song.read()
    return song_service.create_song(
        request=request,
        title=title,
        content=content,
        content_type=song.content_type,
        created_by=created_by,
        genres=genres
    )

@song_router.get("/music/{file_name}", response_class=FileResponse)
async def get_music(file_name: str):
    return song_service.get_music(file_name)

@song_router.get("/{genre}")
async def song_by_genre(genre: str):
    return song_service.song_by_genre(genre)