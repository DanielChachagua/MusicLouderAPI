from fastapi import APIRouter, Depends, Query, UploadFile, File, Request, Form, Body
from fastapi.responses import FileResponse
from ..Models.user_model import User
from ..Routes.auth import get_current_user
from ..Schemas.response_schema import ArtistResponse
from ..Schemas.artist_schema import ArtistDTOResponse, ArtistPaginatedResponse
from ..Services.artist_service import ArtistService

artist_router = APIRouter(tags=['Artists'])

artist_service = ArtistService(path_image='src/Multimedia/Image/Artist')


@artist_router.get('/', response_model=ArtistPaginatedResponse)
async def get_artists(request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> ArtistPaginatedResponse:
    return artist_service.get_artists(request, page, size)


@artist_router.get('/{id}', response_model=ArtistResponse)
async def get_artist(request: Request, id: int) -> ArtistResponse:
    return artist_service.get_artist(request, id)

@artist_router.post('/create', response_model=ArtistDTOResponse)
async def create_artist(
    request: Request,
    name: str = Form(...),
    bio: str = Form(...),
    created_by: int = Form(...),
    image: UploadFile = File(...),
    user: User = Depends(get_current_user)
) -> ArtistDTOResponse:
    return artist_service.create_artist(
        request=request, 
        name = name,
        bio = bio,
        created_by = created_by,
        image=image,
        user=user
    )


@artist_router.put('/{id}', response_model=ArtistDTOResponse)
async def update_artist(
    id: int,
    request: Request,
    name: str = Form(...),
    bio: str = Form(...),
    created_by: int = Form(...),
    image: UploadFile = File(None),
    user: User = Depends(get_current_user)
) -> ArtistDTOResponse:
    return artist_service.update_artist(
        id=id,
        request=request, 
        name = name,
        bio = bio,
        created_by = created_by,
        image=image,
        user=user
    )

@artist_router.delete('/{id}', response_model=dict)
async def delete_artist(id: int,user: User = Depends(get_current_user)) -> dict:
    return artist_service.delete_artist(id, user)


@artist_router.get('/image/{file_name}', response_class=FileResponse)
async def get_image_artist(file_name: str) -> FileResponse:
    return artist_service.get_image_artist(file_name)
