from peewee import *
from datetime import datetime, timezone
from ..Database.configuration import db

class Genre(Model):
    name = CharField(unique=True, max_length=50)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.name

    class Meta:
        database = db
        table_name = 'genres'