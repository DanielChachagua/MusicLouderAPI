from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Request
from ..Models.songs import *
from ..Database.db import *
import math
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from typing import List
from starlette.responses import FileResponse
import uuid

song_router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_MIME_TYPES = [
    "audio/mpeg",  # MP3
    "audio/aac",  # AAC
    "audio/ogg",  # Ogg Vorbis
]

mime_to_extension = {
    "audio/mpeg": ".mp3",
    "audio/acc": ".acc",
    "audio/ogg": ".ogg",
}

@song_router.get('/', response_model=SongPaginatedResponse)
async def get_songs(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)) -> SongPaginatedResponse:
    try:
        offset = (page - 1) * size
        limit = size
        total_count = Song.select().count()
        users_query = Song.select().limit(limit).offset(offset)
        song_list = [SongResponse.model_validate(song) for song in users_query]
        total_pages = math.ceil(total_count / size)
        return {
            "page": page,
            "size": size,
            "total_count": total_count,
            "total_pages": total_pages,
            "songs": song_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    
@song_router.get('/{id}', response_model=SongResponse)
async def get_song(id: int):
    try:
        song = Song.get_by_id(id)
        album = None
        artist = None
        print(song.title)
        if not song:
            raise HTTPException(status_code=404, detail='Cancion no encontrada') 

        if song.album != None:
            albumSong = Album.get_by_id(song.album)
            album = AlbumResponse.model_validate(albumSong)

        if song.artist != None:
            artistSong = Artist.get_by_id(song.artist)
            artist =ArtistResponse.model_validate(artistSong)
            
        genres = (Genre
                .select(Genre)
                .join(SongGenre)
                .where(SongGenre.song == song.id))
        
        user = User.get_by_id(song.created_by)
        
        song_resp = SongResponse(
            title=song.title,
            duration=song.duration,
            url_song=song.url_song,
            album= album,
            artist= artist,
            genres=[GenreResponse.model_validate(genre) for genre in genres],
            created_by=UserInfo.model_validate(user),
            created_at=song.created_at,
            updated_at=song.updated_at

        )
        return song_resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@song_router.post('/create')
async def create_song(
    request: Request,
    title: str = Form(...),
    song: UploadFile = File(...),
    created_by: int = Form(...),
    genres: List[str] = Form(...), 
):
    try:
        # Leer el contenido del archivo una sola vez
        content = await song.read()
        file_size = len(content)

        # Validar el tamaño máximo del archivo
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="El audio no puede exceder los 10MB")
        
        # Validar el tipo MIME del archivo
        if song.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Formato inválido. Los formatos válidos son: MP3, AAC, Ogg Vorbis")
        
        # Crear la carpeta si no existe
        save_path = 'src/Multimedia/Music'
        os.makedirs(save_path, exist_ok=True)
        
        # Definir la ruta completa para guardar el archivo
        file_extension = mime_to_extension.get(song.content_type, "")
        song.filename = f"{uuid.uuid4().hex}{file_extension}"
        file_location = os.path.join(save_path, song.filename)
        base_url = f"{request.url.scheme}://{request.url.netloc}/songs/music/{song.filename}"
        
        # Guardar el archivo
        with open(file_location, "wb") as file_object:
            file_object.write(content)

        # Obtener la duración del archivo de audio
        duration = get_audio_duration(file_location, song.content_type)

        # Crear la instancia de Song
        new_song = Song(
            title=title,
            duration=duration,
            url_song=base_url,
            created_by=created_by
        )
        user = User.get_by_id(created_by)

        # Guardar la canción
        try:
            new_song.save()
        except Exception as e:
            remove_file_if_exists(file_location)
            raise HTTPException(status_code=500, detail="Error al guardar la canción: " + str(e))

        # Asignar géneros a la canción
        genre_list = genres[0].split(',')
        for genre_name in genre_list:
            genre, _ = Genre.get_or_create(name=genre_name.lower())
            SongGenre.create(song=new_song, genre=genre)

        return {
            "message": "Song created successfully",
            "song": {
                "title": new_song.title,
                "duration": new_song.duration,
                "album": new_song.album,
                "created_by": UserInfo.model_validate(user),
                "filename": new_song.title,
                "file_location": base_url,
                "genres": genre_list
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_audio_duration(file_location: str, content_type: str) -> int:
    """Obtiene la duración del archivo de audio basado en su tipo MIME."""
    try:
        if content_type == "audio/mpeg":
            audio = MP3(file_location)
        elif content_type == "audio/flac":
            audio = FLAC(file_location)
        elif content_type == "audio/ogg":
            audio = OggVorbis(file_location)
        elif content_type == "audio/aiff":
            audio = AIFF(file_location)
        else:
            raise HTTPException(status_code=400, detail="Formato de audio no soportado.")
        
        return int(audio.info.length)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer la metadata del archivo: " + str(e))

def remove_file_if_exists(file_location: str):
    """Elimina el archivo si existe."""
    if os.path.exists(file_location):
        os.remove(file_location)

@song_router.get("/music/{file_name}", response_class=FileResponse)
async def get_music(file_name: str):
    try:
        # Construir la ruta completa del archivo
        file_path = os.path.join("src/Multimedia/Music", file_name)

        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Obtener el tipo MIME basado en la extensión del archivo
        file_extension = os.path.splitext(file_name)[1]
        mime_type = {v: k for k, v in mime_to_extension.items()}.get(file_extension, "application/octet-stream")

        # Devolver el archivo
        return FileResponse(file_path, media_type=mime_type, filename=file_name)
    except Exception as e:
        raise HTTPException(500, str(e))