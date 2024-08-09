from fastapi import APIRouter, HTTPException, Query, Request, UploadFile, Response, status
from typing import List, Optional
from datetime import datetime, timezone

from ..Schemas.response_schema import ArtistResponse
from ..Models.album_model import Album
from ..Models.song_model import Song
from ..Models.artist_model import Artist
from ..Models.user_model import User
from ..Services.Tools.image_tool import ImageTool
from ..Schemas.artist_schema import ArtistDTOResponse, ArtistPaginatedResponse
from ..Schemas.album_schema import AlbumDTOResponse
from ..Schemas.user_schema import UserInfo
from ..Schemas.song_schema import SongDTOResponse
from starlette.responses import FileResponse
import math
import os

class ArtistService:
    def __init__(self, path_image):
        self.path_image = path_image


    def get_artists(self, request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> ArtistPaginatedResponse:
        try:
            offset = (page - 1) * size
            limit = size
            total_count = Artist.select().count()
            artist_query = Artist.select().limit(limit).offset(offset)

            artists = [
                ArtistDTOResponse(
                    id= artist.id,
                    name=artist.name,
                    bio=artist.bio or None or '',
                    url_image=f"{request.url.scheme}://{request.url.netloc}/artist/image/{artist.url_image}",
                    created_at=artist.created_at,
                    updated_at=artist.updated_at
                )
                for artist in artist_query
            ]

            total_pages = math.ceil(total_count / size)

            return ArtistPaginatedResponse(
                page=page,
                size=size,
                total_count=total_count,
                total_pages=total_pages,
                artist=artists
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def get_artist(self, request: Request, id: int) -> ArtistResponse:
        try:
            artist = Artist.get_by_id(id)
            albums = Album.select().where(Album.artist == artist.id)
            songs = Song.select().where(Song.artist == artist.id)
            
            return ArtistResponse(
                id=artist.id,
                name=artist.name,
                bio=artist.bio or '',
                url_image=f"{request.url.scheme}://{request.url.netloc}/artist/image/{artist.url_image}",
                songs= [SongDTOResponse.model_validate(song) for song in songs],
                albums=[AlbumDTOResponse.model_validate(album) for album in albums],
                created_by=UserInfo.model_validate(User.get_by_id(artist.created_by)),
                created_at=artist.created_at,
                updated_at=artist.updated_at
            )
        except Artist.DoesNotExist:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def create_artist(self, request: Request, name: str, bio: str, image: UploadFile, user: User) -> ArtistDTOResponse:
        try:
            if Artist.select().where(Artist.name == name):
                raise HTTPException(400, 'El artista ya existe')
            
            image_tool = ImageTool(self.path_image)

            file_name = image_tool.save_image(image, (500, 500))
            
            try:
                new_artist: Artist = Artist.create(
                    name=name,
                    bio=bio,
                    url_image=file_name,
                    created_by=user.id
                )
            except Exception as e:
                image_tool.delete_image(file_name)
                raise HTTPException(status_code=500, detail=f"Error al guardar el artista. Error :{e}")
            
            return ArtistDTOResponse(
                id=new_artist.id,
                name=new_artist.name,
                bio=new_artist.bio,
                url_image=f"{request.url.scheme}://{request.url.netloc}/artist/image/{new_artist.url_image}",
                created_at=new_artist.created_at,
                updated_at=new_artist.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def update_artist(self, id: int, request: Request, name: str, bio: str, image: UploadFile, user: User) -> ArtistDTOResponse:
        try:
            image_tool = ImageTool(self.path_image)

            artist: Artist = Artist.get_by_id(id)
            if artist.created_by.id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No tiene permisos para editar el artista', headers={ 'WWW-Authenticate' : 'Bearer'})
            artist.name = name
            artist.bio = bio
            artist.updated_at = datetime.now(timezone.utc)

            old_image = artist.url_image
            new_image = None
            if image != None:
                new_image = image_tool.save_image(image, (500, 500))
            if new_image != None:
                artist.url_image = new_image
                image_tool.delete_image(old_image)

            artist.save()

            return ArtistDTOResponse(
                id=artist.id,
                name=artist.name,
                bio=artist.bio,
                url_image=f"{request.url.scheme}://{request.url.netloc}/artist/image/{artist.url_image}",
                created_at=artist.created_at,
                updated_at=artist.updated_at
            )
        except Artist.DoesNotExist:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def delete_artist(self, id: int) -> dict:
        try:
            artist: Artist = Artist.get_by_id(id)
            artist.delete_instance()
            ImageTool(self.path_image).delete_image(artist.url_image)
            return {"detail": "Artista eliminado exitosamente"}
        except Artist.DoesNotExist:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def get_image_artist(self, file_name: str) -> FileResponse:
        mime_to_extension = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
        }
        try:
            file_path = os.path.join(self.path_image, file_name)

            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")

            file_extension = os.path.splitext(file_name)[1].lower()
            mime_type = mime_to_extension.get(file_extension, "application/octet-stream")

            return FileResponse(file_path, media_type=mime_type, filename=file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al servir el archivo: {str(e)}")
        
