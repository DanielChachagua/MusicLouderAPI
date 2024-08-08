from datetime import date
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request, status

from ..Schemas.album_schema import AlbumPaginatedResponse, AlbumDTOResponse
from ..Schemas.response_schema import AlbumResponse
from .Tools.image_tool import ImageTool
from ..Schemas.song_schema import *
from ..Database.db import *
from ..Database.configuration import db
import math
import os
from typing import List, Any
from starlette.responses import FileResponse

class AlbumService:
    def __init__(self, path_image: str):
        self.path_image = path_image

    def create_album(self, request: Request, title: str, artist: int, release_date: date, image: UploadFile, user: User) -> AlbumDTOResponse:
        try:
            with db.atomic():
                image_tool = ImageTool(self.path_image)

                file_name = image_tool.save_image(image,(500,500))

                artist_get = Artist.select().where(Artist.id == artist).first()

                exist_artist = None
                if artist_get:
                    exist_artist = artist

                try:
                    album: Album = Album.create(
                        title = title,
                        artist = exist_artist,
                        release_date = release_date,
                        url_image = file_name,
                        created_by = user.id
                    )
                except Exception as e:
                    image_tool.delete_image(file_name)
                    raise HTTPException(status_code=500, detail=f"Error al guardar el album. Error :{e}")
                
                

                return AlbumDTOResponse(
                    id=album.id,
                    title= album.title,
                    release_date = album.release_date,
                    url_image = f"{request.url.scheme}://{request.url.netloc}/artist/image/{album.url_image}",
                    created_at = album.created_at,
                    updated_at = album.updated_at
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_albums(self, request: Request, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> AlbumPaginatedResponse:
        try:
            offset = (page - 1) * size
            limit = size
            total_count = Album.select().count()
            albums_query = Album.select().limit(limit).offset(offset)

            albums: List[AlbumDTOResponse] = [
                AlbumDTOResponse(
                    id=album.id,
                    title=album.title,
                    release_date=album.release_date,
                    created_at = album.created_at,
                    url_image=f"{request.url.scheme}://{request.url.netloc}/artist/image/{album.url_image}",
                    updated_at = album.updated_at
                ) 
                for album in albums_query
            ]

            total_pages = math.ceil(total_count / size)

            return AlbumPaginatedResponse(
                page=page,
                size=size,
                total_count=total_count,
                total_pages=total_pages,
                albums=albums
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_album(self, request: Request, id: int) -> AlbumResponse:
        try:
            album: Album = Album.get_by_id(id)
            album.url_image = f"{request.url.scheme}://{request.url.netloc}/artist/image/{album.url_image}"
            return album
        except Album.DoesNotExist:
            raise HTTPException(status_code=404, detail='Album no encontrado')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def update_album(self, request: Request, id: int, title: str, artist: int, release_date: date, image: UploadFile, user: User) -> AlbumDTOResponse:
        try:
            with db.atomic():
                try:
                    album: Album = Album.get_by_id(id)
                except Album.DoesNotExist:
                    raise HTTPException(status_code=404, detail='Album no encontrado')

                if album.created_by.id != user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No posee el permiso para editar el album', headers={ 'WWW-Authenticate' : 'Bearer'})
                album.title = title

                try:
                    artist_instance = Artist.get_by_id(artist)
                    album.artist = artist_instance
                except Artist.DoesNotExist:
                    raise HTTPException(status_code=404, detail='Artista no encontrado')

                album.release_date = release_date

                image_tool = ImageTool(self.path_image)
                old_image = album.url_image
                new_image = None
                if image:
                    new_image = image_tool.save_image(image, (500, 500))
                    if new_image:
                        album.url_image = new_image
                        image_tool.delete_image(old_image)

                album.save()

                album.url_image = f"{request.url.scheme}://{request.url.netloc}/artist/image/{album.url_image}"

                return album
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error de integridad en la base de datos")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    def delete_album(self, id: int, user: User) -> Any:
        try:
            album: Album = Album.get_by_id(id)
            if album.created_by.id != user.id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No posee el permiso para editar el album', headers={ 'WWW-Authenticate' : 'Bearer'})
            album.delete_instance()
            ImageTool(self.path_image).delete_image(album.url_image)
            return status.HTTP_200_OK
        except Album.DoesNotExist:
            raise HTTPException(status_code=404, detail="Album no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def get_image_album(self, file_name: str) -> FileResponse:
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
        