import os
import uuid
from fastapi import HTTPException
from mutagen.mp3 import MP3
from mutagen.aac import AAC
from mutagen.oggvorbis import OggVorbis

class SongTool:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_MIME_TYPES = [
        "audio/mpeg",
        "audio/aac",
        "audio/ogg",
    ]
    mime_to_extension = {
        "audio/mpeg": ".mp3",
        "audio/aac": ".aac",
        "audio/ogg": ".ogg",
    }

    def __init__(self, path_song: str) -> None:
        self.path_song = path_song
        os.makedirs(self.path_song, exist_ok=True)

    def reset_name_song(self, filename: str) -> str:
        """Genera un nuevo nombre de archivo si ya existe uno con el mismo nombre."""
        if not os.path.exists(os.path.join(self.path_song, filename)):
            return filename
        nombre, extension = os.path.splitext(filename)
        nuevo_nombre = f"{uuid.uuid4()}{extension}"
        return nuevo_nombre

    def save_song(self, content_type: str, content: bytes) -> tuple[str, int]:
        """Guarda el archivo de audio en el disco y retorna el nombre del archivo y su duración."""
        file_size = len(content)

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="El audio no puede exceder los 10MB")
        
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Formato inválido. Los formatos válidos son: MP3, AAC, Ogg Vorbis")

        file_extension = self.mime_to_extension.get(content_type, "")
        filename = f"{uuid.uuid4().hex}{file_extension}"
        file_location = os.path.join(self.path_song, filename)

        try:
            with open(file_location, "wb") as file_object:
                file_object.write(content)
            duration = self.get_audio_duration(file_location, content_type)
        except Exception as e:
            self.delete_song(filename)
            raise HTTPException(status_code=500, detail=f"Error al guardar el audio: {str(e)}")
        
        return filename, duration
    
    def delete_song(self, filename: str) -> None:
        """Elimina el archivo de audio especificado del disco."""
        media_path = os.path.join(self.path_song, filename)
        if os.path.exists(media_path):
            os.remove(media_path)
        else:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")

    def get_audio_duration(self, path: str, content_type: str) -> int:
        """Obtiene la duración del archivo de audio en segundos."""
        try:
            if content_type == "audio/mpeg":
                audio = MP3(path)
            elif content_type == "audio/aac":
                audio = AAC(path)
            elif content_type == "audio/ogg":
                audio = OggVorbis(path)
            else:
                raise HTTPException(status_code=400, detail="Formato de audio no soportado.")
            return int(audio.info.length)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al leer la metadata del archivo: {str(e)}")
