from datetime import date
from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from fastapi.responses import FileResponse

from ..Schemas.response_schema import AlbumResponse

from ..Schemas.album_schema import AlbumPaginatedResponse, AlbumDTOResponse
from ..Services.album_service import AlbumService

album_router = APIRouter()

album_service = AlbumService(path_image='src/Multimedia/Image/Album')

@album_router.get('/', response_model=AlbumPaginatedResponse)
async def get_albums(request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> AlbumPaginatedResponse:
    return album_service.get_albums(request, page, size)


@album_router.get('/{id}', response_model=AlbumResponse)
async def get_album(request: Request, id: int) -> AlbumResponse:
    return album_service.get_album(request, id)

@album_router.post('/create', response_model=AlbumDTOResponse)
async def create_album(
    request: Request, 
    title: str = Form(...), 
    artist: int = Form(None), 
    release_date: date = Form(...), 
    created_by: int = Form(...), 
    image: UploadFile = File(...)
) -> AlbumDTOResponse:
    return album_service.create_album(
        request=request, 
        title= title,
        artist= artist,
        release_date= release_date,
        created_by = created_by,
        image=image
    )


@album_router.put('/{id}', response_model=AlbumDTOResponse)
async def update_album(
    request: Request,
    id: int,
    title: str = Form(...),
    artist: int = Form(...),
    release_date: date = Form(...),
    image: UploadFile = File(None)
) -> AlbumDTOResponse:
    return album_service.update_album(
        request=request, 
        id=id,
        title= title,
        artist= artist,
        release_date= release_date,
        image=image
    )

@album_router.delete('/{id}', response_model=dict)
async def delete_artist(id: int) -> dict:
    return album_service.delete_album(id)


@album_router.get('/image/{file_name}', response_class=FileResponse)
async def get_image_artist(file_name: str) -> FileResponse:
    return album_service.get_image_album(file_name)
