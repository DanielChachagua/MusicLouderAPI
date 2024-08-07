from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request

from src.Schemas.user_schema import UserInfo

from ..Schemas.response_schema import PlayListResponse
from ..Models.playlist_model import Playlist, PlaylistSong
from ..Schemas.playlist_schema import PlayListDTOResponse, PlayListRequest
from ..Schemas.song_schema import *
from ..Database.configuration import db
from ..Database.db import *
from peewee import IntegrityError

class PlaylistService:

    def create_playlist(self, playlist: PlayListRequest) -> PlayListDTOResponse:
        try:
            with db.atomic():
                try:
                    user = User.get_by_id(playlist.created_by)
                except User.DoesNotExist:
                    raise HTTPException(status_code=404, detail="User no encontrado")

                try:
                    new_playlist = Playlist.create(
                        name=playlist.name,
                        created_by=user,  # Utilizar el objeto user
                    )

                    for song_id in playlist.songs:
                        try:
                            song = Song.get_by_id(song_id)
                            PlaylistSong.create(playlist=new_playlist, song=song)
                        except Song.DoesNotExist:
                            raise HTTPException(status_code=404, detail=f"Cancion con {song_id} no encontrado")
                        except IntegrityError:
                            raise HTTPException(status_code=400, detail=f"Error al intentar agregar cancion de ID {song_id} a la playlist")

                    return PlayListDTOResponse.model_validate(new_playlist)
                except IntegrityError as e:
                    raise HTTPException(status_code=400, detail="Error al crear la playlist")
        except Exception as e:
            raise HTTPException(500, str(e))
        

    def get_playlists(self, id:int) -> PlayListDTOResponse:
        try:
            try:
                user: User = User.get_by_id(id)
            except User.DoesNotExist:
                raise HTTPException(status_code=404, detail="User no encontrado")
            
            playlists: List[Playlist] = Playlist.select().where(Playlist.created_by == user.id)

            return playlists
        except Exception as e:
            raise HTTPException(500, str(e))
        
    
    def get_playlist(self, id: int, user_id: int) -> PlayListResponse:
        try:
            user = User.get_or_none(User.id == user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User no encontrado")

            playlist = Playlist.get_or_none(Playlist.id == id)
            if not playlist:
                raise HTTPException(status_code=404, detail="PlayList no encontrado")

            if playlist.created_by.id != user.id:
                raise HTTPException(status_code=403, detail="Forbidden")

            songs = Song.select().join(PlaylistSong).where(PlaylistSong.playlist == playlist)
            song_dto_responses = [SongDTOResponse.model_validate(song) for song in songs]

            playlist_response: PlayListResponse = PlayListResponse(
                id=playlist.id,
                name=playlist.name,
                songs=song_dto_responses,
                created_by=UserInfo.model_validate(playlist.created_by),
                created_at=playlist.created_at,
                updated_at=playlist.updated_at
            )

            return playlist_response

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def delete_playlist(self, id: int, user_id: int):
        try:
            playlist = Playlist.get_by_id(id)
            if playlist.created_by.id != user_id:
                raise HTTPException(status_code=403, detail="Forbidden")

            with db.atomic():
                PlaylistSong.delete().where(PlaylistSong.playlist == playlist).execute()
                playlist.delete_instance()

            return PlayListDTOResponse.model_validate(playlist)
        except Playlist.DoesNotExist:
            raise HTTPException(status_code=404, detail="PlayList no encontrado")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    def edit_playlist(self, id: int, playlist: PlayListRequest) -> PlayListDTOResponse:
        try:
            with db.atomic():
                try:
                    user = User.get_by_id(playlist.created_by)
                except User.DoesNotExist:
                    raise HTTPException(status_code=404, detail="User no encontrado")

                try:
                    existing_playlist = Playlist.get_by_id(id)
                except Playlist.DoesNotExist:
                    raise HTTPException(status_code=404, detail="PlayList no encontrado")

                existing_playlist.name = playlist.name
                existing_playlist.updated_at = datetime.now(timezone.utc)
                existing_playlist.save()

                PlaylistSong.delete().where(PlaylistSong.playlist == existing_playlist).execute()

                for song_id in playlist.songs:
                    try:
                        song = Song.get_by_id(song_id)
                        PlaylistSong.create(playlist=existing_playlist, song=song)
                    except Song.DoesNotExist:
                        raise HTTPException(status_code=404, detail=f"Cancion con ID {song_id} no encontrado")
                    except IntegrityError:
                        raise HTTPException(status_code=400, detail=f"Error al intentar agregar cancion de ID {song_id} a la playlist")

                return PlayListDTOResponse.model_validate(existing_playlist)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail="Error al editar la playlist")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
