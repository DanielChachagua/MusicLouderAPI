from fastapi import FastAPI
from contextlib import asynccontextmanager
from .Database.db import create_database_if_not_exists
from .Database.configuration import db
from .Middleware.timing import TimingMiddleware
from .Routes.auth import auth_router
from .Routes.user_router import user_router
from .Routes.song_router import song_router
from .Routes.album_router import album_router
from .Routes.artist_router import artist_router
from .Routes.playlist_router import playlist_router
from .Models.song_model import Song, SongGenre
from .Models.album_model import Album
from .Models.artist_model import Artist
from .Models.user_model import User
from .Models.genre_model import Genre
from .Models.playlist_model import Playlist, PlaylistSong
import logging


app = FastAPI(title= 'API para app MUSICLOUDER',
            description='API para CRUD de usuarios y canciones',
            version='0.0.1')

app.include_router(prefix= '/auth', router= auth_router)
app.include_router(prefix= '/user', router= user_router)
app.include_router(prefix= '/songs', router= song_router)
app.include_router(prefix= '/album', router= album_router)
app.include_router(prefix= '/artist', router= artist_router)
app.include_router(prefix= '/playlist', router= playlist_router)

app.add_middleware(TimingMiddleware)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_if_not_exists()  # Asegúrate de que la base de datos está creada
    if db.is_closed():
        logging.info("Conectando a la base de datos...")
        db.connect()
        logging.info("Conexión creada.")
    logging.info('Validando tablas...')
    db.create_tables([User, Artist, Album, Genre, Song, Playlist, PlaylistSong, SongGenre])
    logging.info('Tablas validadas.')
    yield
    if not db.is_closed():
        logging.info("Cerrando la base de datos...")
        db.close()
        logging.info("Base de datos cerrada.")
        logging.info("El servidor se está cerrando.")


app.router.lifespan_context = lifespan
