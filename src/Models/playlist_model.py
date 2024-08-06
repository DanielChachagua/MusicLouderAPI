from peewee import *
from datetime import datetime, timezone
from ..Models.song_model import Song
from ..Models.user_model import User
from ..Database.configuration import db

class Playlist(Model):
    name = CharField(max_length=100)
    created_by = ForeignKeyField(User, backref='playlists')
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))


    class Meta:
        database = db
        table_name = 'playlists'

class PlaylistSong(Model):
    playlist = ForeignKeyField(Playlist, backref='songs')
    song = ForeignKeyField(Song, backref='playlists')

    class Meta:
        database = db
        table_name = 'playlist_songs'