from fastapi import FastAPI
from contextlib import asynccontextmanager
from .Database.db import *
from .Middleware.timing import TimingMiddleware
from .Routes.user_router import user_router
from .Routes.song_router import song_router

app = FastAPI(title= 'API para app MUSICLOUDER',
            description='API para CRUD de usuarios y canciones',
            version='0.0.1')

app.include_router(prefix= '/user', router= user_router)
app.include_router(prefix= '/song', router= song_router)

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
