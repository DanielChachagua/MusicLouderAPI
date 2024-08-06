from fastapi import APIRouter

from ..Services.playlist_service import PlaylistService

playlist_router = APIRouter()

playlist_service = PlaylistService()