from fastapi import APIRouter, Depends
from typing import List

from ..Models.user_model import User
from ..Routes.auth import get_current_user
from ..Schemas.playlist_schema import PlayListDTOResponse, PlayListRequest
from ..Schemas.response_schema import PlayListResponse
from ..Services.playlist_service import PlaylistService

playlist_router = APIRouter()

playlist_service = PlaylistService()

@playlist_router.get('/', response_model=List[PlayListDTOResponse])
async def get_playlists(user: User = Depends(get_current_user)) -> List[PlayListDTOResponse]:
    return playlist_service.get_playlists(user)


@playlist_router.get('/{id}', response_model=PlayListResponse)
async def get_playlist(id:int, user: User = Depends(get_current_user)) -> PlayListResponse:
    return playlist_service.get_playlist(id= id, user=user)

@playlist_router.post('/create', response_model=PlayListDTOResponse)
async def create_playlist(playlist: PlayListRequest,user: User = Depends(get_current_user)) -> PlayListDTOResponse:
    return playlist_service.create_playlist(playlist=playlist, user=user)


@playlist_router.put('/{id}', response_model=PlayListDTOResponse)
async def create_playlist(id: int, playlist: PlayListRequest, user: User = Depends(get_current_user)) -> PlayListDTOResponse:
    return playlist_service.edit_playlist(id=id, playlist=playlist, user=user)


@playlist_router.delete('/{id}', response_model=PlayListDTOResponse)
async def delete_playlist(id: int, user: User = Depends(get_current_user)) -> PlayListDTOResponse:
    return playlist_service.delete_playlist(id, user)
