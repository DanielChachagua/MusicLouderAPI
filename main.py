from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import *
from Middleware.timing import TimingMiddleware

app = FastAPI(title= 'API para app MUSICLOUDER',
            description='API para CRUD de usuarios y canciones',
            version='1')

@asynccontextmanager
async def lifespan(app: FastAPI):
    if db.is_closed():
        logging.info("Conectando a la base de datos...")
        db.connect()
        logging.info("Coneccion creada.")
    create_database_if_not_exists()
    logging.info("El servidor ha iniciado.")

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
app.add_middleware(TimingMiddleware)

@app.get('/')
async def index():
    return 'hola'

@app.get('/sobre')
async def sobre():
    return 'sobre'
