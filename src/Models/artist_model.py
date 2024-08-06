from peewee import *
from datetime import datetime, timezone
from ..Models.user_model import User
from ..Database.configuration import db

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