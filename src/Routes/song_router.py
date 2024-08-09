from typing import List
from fastapi import APIRouter, Query, UploadFile, File, Form, Request, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..Models.user_model import User
from ..Schemas.response_schema import SongResponse
from ..Schemas.song_schema import SongPaginatedResponse, SongDTOResponse
from ..Services.song_service import SongService
from ..Routes.auth import get_current_user

song_router = APIRouter(tags=['Songs'])

song_service = SongService(path_song='src/Multimedia/Music')

@song_router.get('/', response_model=SongPaginatedResponse, summary="Get All Songs", description="Retrieve a list of songs.")
async def get_songs(request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> SongPaginatedResponse:
    return song_service.get_songs(request, page, size)

@song_router.get('/{id}', response_model=SongResponse)
async def get_song(request: Request, id: int):
    return song_service.get_song(request, id)

@song_router.post('/create')
async def create_song(request: Request,
    title: str = Form(...),
    song: UploadFile = File(...),
    genres: List[str] = Form(...),
    album: int = Form(None),
    artist: int = Form(None),
    user: User = Depends(get_current_user)
):
    content = await song.read()
    return song_service.create_song(
        request=request,
        user=user,
        title=title,
        content=content,
        content_type=song.content_type,
        genres=genres,
        album=album,
        artist=artist
    )

@song_router.get("/music/{file_name}", response_class=FileResponse)
async def get_music(file_name: str):
    return song_service.get_music(file_name)

@song_router.get("/genre/{genre}", response_model=SongPaginatedResponse)
async def songs_by_genre(request: Request, genre: str, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> SongPaginatedResponse:
    return song_service.songs_by_genre(request=request, genre=genre, page=page, size=size)

@song_router.get("/filter/{title}", response_model=List[SongDTOResponse])
async def get_filter_songs(request: Request, title: str):
    return song_service.get_filter_songs(request=request, title=title)

@song_router.delete("/{song_id}", response_model=int)
async def delete_song(song_id: int, user: User = Depends(get_current_user)):
    return song_service.delete_song(song_id=song_id, user=user)

@song_router.put("/{song_id}", response_model=SongDTOResponse)
async def edit_song(
    request: Request, 
    song_id: int, 
    user: User = Depends(get_current_user), 
    title: str = None, 
    song: UploadFile = File(None), 
    genres: List[str] = Form(None),
    album: int = Form(None),
    artist: int = Form(None)
):  
    content = None
    content_type = None
    if song:
        content = await song.read()
        content_type = song.content_type
    return song_service.edit_song(
        request=request, 
        song_id=song_id, 
        user=user, 
        title=title, 
        content=content,
        content_type=content_type,
        genres=genres,
        album=album,
        artist=artist
    )
   