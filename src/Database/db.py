#db.py

from peewee import *
import MySQLdb
import logging
from datetime import datetime, timezone
from playhouse.signals import pre_save
from decouple import config
# Configuración de la base de datos


# Conectar al servidor MySQL para crear la base de datos si no existe
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

# Inicializar la base de datos de Peewee
db = MySQLDatabase(
    config('DB_NAME'),
    host=config('DB_HOST'),
    user=config('DB_USER'),
    passwd=config('DB_PASSWORD'),
    port=int(config('DB_PORT'))
)

#Modelo User
class User(Model):
    username = CharField(max_length= 50, unique= True)
    email = CharField(max_length= 50, unique= True)
    valid_mail = BooleanField(default=False)
    password_hash = CharField(max_length=100)
    first_name = CharField(max_length= 50)
    last_name = CharField(max_length= 50)
    date_of_birth = DateField()
    url_image = CharField(null= True)
    is_active = BooleanField(default=False)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.username

    class Meta:
        database = db
        table_name = 'users'  

# Modelo de artista
class Artist(Model):
    name = CharField(unique=True, max_length=100)
    bio = TextField(null=True)
    url_image = CharField()
    created_by = ForeignKeyField(User, backref='artists')
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.name

    class Meta:
        database = db
        table_name = 'artists'

# Modelo de álbum
class Album(Model):
    title = CharField(max_length=100)
    artist = ForeignKeyField(Artist, backref='albums', null = True)
    release_date = DateField(null=True)
    url_image = CharField()
    created_by = ForeignKeyField(User, backref='albums')
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.title

    class Meta:
        database = db
        table_name = 'albums'

# Modelo de género
class Genre(Model):
    name = CharField(unique=True, max_length=50)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.name

    class Meta:
        database = db
        table_name = 'genres'

# Modelo de canción
class Song(Model):
    title = CharField(max_length=100)
    duration = IntegerField()  # Duración en segundos
    url_song = CharField(max_length=100)
    album = ForeignKeyField(Album, backref='songs', null = True)
    artist = ForeignKeyField(Artist, backref='songs', null = True)
    created_by = ForeignKeyField(User, backref='songs')
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.title
    
    class Meta:
        database = db
        table_name = 'songs'

# Relación many-to-many para canciones y géneros
class SongGenre(Model):
    song = ForeignKeyField(Song, backref='genres')
    genre = ForeignKeyField(Genre, backref='songs')

    class Meta:
        database = db
        table_name = 'song_genres'

# Modelo de lista de reproducción
class Playlist(Model):
    name = CharField(max_length=100)
    created_by = ForeignKeyField(User, backref='playlists')
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


    class Meta:
        database = db
        table_name = 'playlists'

# Relación many-to-many para canciones y listas de reproducción
class PlaylistSong(Model):
    playlist = ForeignKeyField(Playlist, backref='songs')
    song = ForeignKeyField(Song, backref='playlists')

    class Meta:
        database = db
        table_name = 'playlist_songs'

# Definición de la señal para actualizar `updated_at`
@pre_save()
def on_save_handler(sender, instance, created):
    instance.updated_at = datetime.now(lambda: datetime.now(timezone.utc))

models = [User, Artist, Album, Genre, Song, Playlist]
for model in models:
    pre_save.connect(on_save_handler, sender=model)


