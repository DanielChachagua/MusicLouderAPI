#db.py

from peewee import *
import MySQLdb
import logging
from datetime import datetime, timezone
from playhouse.signals import pre_save
from decouple import config
from ..Models.album_model import Album
from ..Models.artist_model import Artist
from ..Models.genre_model import Genre
from ..Models.playlist_model import Playlist
from ..Models.song_model import Song
from ..Models.user_model import User

def create_database_if_not_exists():
    connection = MySQLdb.connect(
        host=config('DB_HOST'),
        user=config('DB_USER'),
        passwd=config('DB_PASSWORD'),
        port= int(config('DB_PORT'))
    )
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config('DB_NAME')}")
        logging.info('Creando base de datos...')
        connection.commit()
        logging.info('Base de datos creada')
    finally:
        cursor.close()
        connection.close()

# db = MySQLDatabase(
#     config('DB_NAME'),
#     host=config('DB_HOST'),
#     user=config('DB_USER'),
#     passwd=config('DB_PASSWORD'),
#     port=int(config('DB_PORT'))
# )

@pre_save()
def on_save_handler(sender, instance, created):
    instance.updated_at = datetime.now(lambda: datetime.now(timezone.utc))

models = [User, Artist, Album, Genre, Song, Playlist]
for model in models:
    pre_save.connect(on_save_handler, sender=model)


