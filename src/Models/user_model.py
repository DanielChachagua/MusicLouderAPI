from peewee import *
from datetime import datetime, timezone
from ..Database.configuration import db
import bcrypt

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

    @classmethod
    def authenticate(cls, email, password):
        user: User = cls. select().where(User.username == email).first()
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None

    def __str__(self):
        return self.username

    class Meta:
        database = db
        table_name = 'users'  