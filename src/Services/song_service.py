import os
import math
from typing import List, Optional
from fastapi import HTTPException, Request, status
from starlette.responses import FileResponse
from ..Schemas.artist_schema import ArtistDTOResponse
from ..Schemas.response_schema import AlbumDTOResponse, GenreDTOResponse, SongResponse
from .Tools.song_tool import SongTool
from ..Schemas.song_schema import SongDTOResponse, SongPaginatedResponse, AlbumDTO, ArtistDTO
from ..Schemas.user_schema import UserInfo
from ..Models.song_model import Song, SongGenre
from ..Models.album_model import Album
from ..Models.artist_model import Artist
from ..Models.user_model import User
from ..Models.genre_model import Genre
from datetime import datetime, timezone

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
                album = None
                artist = None
                if song.album is not None:
                    album = Album.get_by_id(song.album)
                    album = AlbumDTO.model_validate(album)

                if song.artist is not None:
                    artist = Artist.get_by_id(song.artist)
                    artist = ArtistDTO.model_validate(artist)

                song_resp: SongDTOResponse = SongDTOResponse(
                    id=song.id,
                    title=song.title,
                    duration=song.duration,
                    url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                    album=album,
                    artist=artist,
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

    def create_song(self, request: Request, title: str, genres: List[str], content: bytes, content_type: str,  user: User, album: int = None, artist: int = None) -> dict:
        try:
            song_tool = SongTool(self.path_song)
            filename, duration = song_tool.save_song(content_type, content)

            try:  
                album = Album.get_by_id(album)
            except:    
                album = None

            try:  
                artist = Artist.get_by_id(artist)
            except:    
                artist = None

            new_song = Song(
                title=title,
                duration=duration,
                album=album,
                artist=artist,
                url_song=filename,
                created_by=user.id
            )
            try:
                new_song.save()

                for genre_name in genres[0].split(','):
                    genre, _ = Genre.get_or_create(name=genre_name.lower())
                    SongGenre.create(song=new_song, genre=genre)
            except Exception as e:
                song_tool.delete_song(filename)
                raise HTTPException(status_code=500, detail=f"Error al guardar el audio: {e}")

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
            file_extension = os.path.splitext(file_name)[1]
            mime_type = {v: k for k, v in mime_to_extension.items()}.get(file_extension, "application/octet-stream")

            return FileResponse(file_path, media_type=mime_type, filename=file_name)
        except Exception as e:
            raise HTTPException(500, str(e))

    def songs_by_genre(self, request: Request, genre: str, page: int, size: int) -> SongPaginatedResponse:
        try:
            genre = Genre.get_or_none(Genre.name == genre)
            if not genre:
                raise HTTPException(status_code=404, detail="Género no encontrado")

            offset = (page - 1) * size
            limit = size

            song_query = (Song
                        .select()
                        .join(SongGenre)
                        .join(Genre)
                        .where(Genre.id == genre.id)
                        .limit(limit)
                        .offset(offset))

            total_count = (Song
                        .select()
                        .join(SongGenre)
                        .join(Genre)
                        .where(Genre.id == genre.id)
                        .count())

            songs = []
            for song in song_query:
                album = None
                artist = None
                if song.album is not None:
                    album = Album.get_by_id(song.album)
                    album = AlbumDTO.model_validate(album)

                if song.artist is not None:
                    artist = Artist.get_by_id(song.artist)
                    artist = ArtistDTO.model_validate(artist)
                song_resp: SongDTOResponse = SongDTOResponse(
                    id=song.id,
                    title=song.title,
                    duration=song.duration,
                    url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                    album=album,
                    artist=artist,
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
        
    def get_filter_songs(self, request: Request, title: str) -> List[SongDTOResponse]:
        try:
            song_query = Song.select().where(Song.title.contains(title)).limit(5)

            songs = []
            for song in song_query:
                album = None
                artist = None
                if song.album is not None:
                    album = Album.get_by_id(song.album)
                    album = AlbumDTO.model_validate(album)

                if song.artist is not None:
                    artist = Artist.get_by_id(song.artist)
                    artist = ArtistDTO.model_validate(artist)

                song_resp: SongDTOResponse = SongDTOResponse(
                    id=song.id,
                    title=song.title,
                    duration=song.duration,
                    url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                    album=album,
                    artist=artist,
                    created_at=song.created_at,
                    updated_at=song.updated_at
                )
                songs.append(song_resp)

            return songs
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    
    def delete_song(self, song_id: int, user: User) -> int:
        try:
            song: Song = Song.get_by_id(song_id)
            if song.created_by.id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No posee el permiso para eliminar esta canción', headers={'WWW-Authenticate': 'Bearer'})
            tool_song = SongTool(self.path_song)
            SongGenre.delete().where(SongGenre.song == song).execute()

            song.delete_instance()

            tool_song.delete_song(song.url_song)

            return status.HTTP_200_OK
        except Song.DoesNotExist:
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

    def edit_song(self, request: Request, song_id: int, user: User, title: Optional[str] = None, album: Optional[int] = None, artist: Optional[int] = None, content: Optional[bytes] = None, content_type: Optional[str] = None, genres: Optional[List[str]] = None) -> SongDTOResponse:
        try:
            song = Song.get_by_id(song_id)

            if song.created_by.id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No posee el permiso para editar esta canción', headers={'WWW-Authenticate': 'Bearer'})

            if title:
                song.title = title

            if album:
                try:
                    album = Album.get_by_id(album)
                except Album.DoesNotExist:
                    album = None

            if artist:
                try:
                    artist = Artist.get_by_id(artist)
                except Artist.DoesNotExist:
                    artist = None

            song_tool = SongTool(self.path_song)

            if content and content_type:
                song_tool.delete_song(song.url_song)
                filename, duration = song_tool.save_song(content_type, content)
                song.url_song = filename
                song.duration = duration

            song.album = album
            song.artist = artist
            song.updated_at = datetime.now(timezone.utc)
            song.save()

            if genres:
                SongGenre.delete().where(SongGenre.song == song).execute()
                for genre_name in genres[0].split(','):
                    genre, _ = Genre.get_or_create(name=genre_name.lower())
                    SongGenre.create(song=song, genre=genre)

            # Verifica que el objeto retornado cumpla con SongDTOResponse
            return SongDTOResponse(
                id=song.id,
                title=song.title,
                duration=song.duration,
                url_song=f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.url_song}",
                album=AlbumDTO.model_validate(album),
                artist=ArtistDTO.model_validate(artist),
                created_at=song.created_at,
                updated_at=song.updated_at
            )

        except Song.DoesNotExist:
            raise HTTPException(status_code=404, detail="Canción no encontrada")
        except Album.DoesNotExist:
            raise HTTPException(status_code=404, detail="Álbum no encontrado")
        except Artist.DoesNotExist:
            raise HTTPException(status_code=404, detail="Artista no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))