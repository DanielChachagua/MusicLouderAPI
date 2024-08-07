from fastapi import APIRouter, Query
from typing import List
from ..Schemas.playlist_schema import PlayListDTOResponse, PlayListRequest
from ..Schemas.response_schema import PlayListResponse
from ..Services.playlist_service import PlaylistService

playlist_router = APIRouter()

playlist_service = PlaylistService()

@playlist_router.get('/', response_model=List[PlayListDTOResponse])
async def get_playlists(id: int) -> List[PlayListDTOResponse]:
    return playlist_service.get_playlists(id)


@playlist_router.get('/{id}', response_model=PlayListResponse)
async def get_playlist(id:int, user_id:int) -> PlayListResponse:
    return playlist_service.get_playlist(id= id, user_id=user_id)

@playlist_router.post('/create', response_model=PlayListDTOResponse)
async def create_playlist(playlist: PlayListRequest) -> PlayListDTOResponse:
    return playlist_service.create_playlist(playlist=playlist)


@playlist_router.put('/{id}', response_model=PlayListDTOResponse)
async def create_playlist(id: int, playlist: PlayListRequest) -> PlayListDTOResponse:
    return playlist_service.edit_playlist(id=id, playlist=playlist)


@playlist_router.delete('/{id}', response_model=PlayListDTOResponse)
async def delete_playlist(id: int) -> PlayListDTOResponse:
    return playlist_service.delete_playlist(id)
