from peewee import *
from datetime import datetime, timezone
from ..Models.user_model import User
from ..Models.artist_model import Artist
from ..Database.configuration import db

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