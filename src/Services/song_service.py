import os
import uuid
import math
from typing import List
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from fastapi import HTTPException, Request
from starlette.responses import FileResponse

from ..Schemas.artist_schema import ArtistDTOResponse
from ..Schemas.response_schema import AlbumDTOResponse, GenreDTOResponse, SongResponse
from .Tools.song_tool import SongTool
from ..Schemas.song_schema import SongDTOResponse, SongPaginatedResponse
from ..Schemas.user_schema import UserInfo
from ..Models.song_model import Song, SongGenre
from ..Models.album_model import Album
from ..Models.artist_model import Artist
from ..Models.user_model import User
from ..Models.genre_model import Genre

class SongService:
    def __init__(self, path_song: str):
        self.path_song = path_song
        
    def get_songs(self, request: Request, page: int, size: int) -> SongPaginatedResponse:
        try:
            offset = (page - 1) * size
            limit = size
            total_count = Song.select().count()
            song_query = Song.select().limit(limit).offset(offset)

            songs = []
            for song in song_query:
                song_resp: SongDTOResponse = SongDTOResponse(
                    id=song.id,
                    title=song.title,
                    duration=song.duration,
                    url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                    created_at=song.created_at,
                    updated_at=song.updated_at
                )
                songs.append(song_resp)

            total_pages = math.ceil(total_count / size)

            return SongPaginatedResponse(
                page=page,
                size=size,
                total_count=total_count,
                total_pages=total_pages,
                songs=songs
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_song(self, request: Request, id: int) -> SongResponse:
        try:
            song = Song.get_by_id(id)
            album = None
            artist = None

            if song.album is not None:
                album = Album.get_by_id(song.album)
                album = AlbumDTOResponse.model_validate(album)

            if song.artist is not None:
                artist = Artist.get_by_id(song.artist)
                artist = ArtistDTOResponse.model_validate(artist)

            genres = (Genre
                    .select(Genre)
                    .join(SongGenre)
                    .where(SongGenre.song == song.id))

            user = User.get_by_id(song.created_by)

            return SongResponse(
                id=song.id,
                title=song.title,
                duration=song.duration,
                url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                album=album,
                artist=artist,
                genres=[GenreDTOResponse.model_validate(genre) for genre in genres],
                created_by=UserInfo.model_validate(user),
                created_at=song.created_at,
                updated_at=song.updated_at
            )
        except Song.DoesNotExist:
            raise HTTPException(status_code=404, detail='Canción no encontrada')
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def create_song(self, request: Request, title: str, content: bytes, content_type: str, created_by: int, genres: List[str]) -> dict:
        try:
            song_tool = SongTool(self.path_song)
            filename, duration = song_tool.save_song(content_type, content)

            new_song = Song(
                title=title,
                duration=duration,
                url_song=filename,
                created_by=created_by
            )
            try:
                user = User.get_by_id(created_by)
                new_song.save()

                for genre_name in genres[0].split(','):
                    genre, _ = Genre.get_or_create(name=genre_name.lower())
                    SongGenre.create(song=new_song, genre=genre)
            except:
                song_tool.delete_song(filename)
                raise HTTPException(status_code=500, detail="Error al guardar el audio")

            return {
                "message": "Cancion creada exitosamente",
                "song": {
                    "title": new_song.title,
                    "duration": new_song.duration,
                    "album": new_song.album,
                    "created_by": UserInfo.model_validate(user),
                    "filename": filename,
                    "file_location": f"{request.url.scheme}://{request.url.netloc}/songs/music/{new_song.url_song}",
                    "genres": genres
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def get_music(self, file_name: str):
        try:
            file_path = os.path.join(self.path_song, file_name)

            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Archivo no encontrado")

            mime_to_extension = {
                "audio/mpeg": ".mp3",
                "audio/aac": ".aac",
                "audio/ogg": ".ogg",
            }
            # Obtener el tipo MIME basado en la extensión del archivo
            file_extension = os.path.splitext(file_name)[1]
            mime_type = {v: k for k, v in mime_to_extension.items()}.get(file_extension, "application/octet-stream")

            # Devolver el archivo
            return FileResponse(file_path, media_type=mime_type, filename=file_name)
        except Exception as e:
            raise HTTPException(500, str(e))

    def song_by_genre(self, genre: str):
        return genre