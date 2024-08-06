from peewee import *
from datetime import datetime, timezone
from ..Models.album_model import Album
from ..Models.artist_model import Artist
from ..Models.genre_model import Genre
from ..Models.user_model import User
from ..Database.configuration import db

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

class SongGenre(Model):
    song = ForeignKeyField(Song, backref='genres')
    genre = ForeignKeyField(Genre, backref='songs')

    class Meta:
        database = db
        table_name = 'song_genres'