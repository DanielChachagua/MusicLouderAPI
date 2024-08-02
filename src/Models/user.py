from pydantic import BaseModel, field_validator
from datetime import date, datetime, timezone
import bcrypt

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    date_of_birth: date
   
    @field_validator('username')
    def username_validator(cls, username):
        if len(username) < 3 or len(username) > 10:
            raise ValueError('El username debe contener entre 3 y 10 caracteres')
        if ' ' in username:
            raise ValueError('El username no puede contener espacios')
        return username

class UserInfo(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class Login(BaseModel):
    email: str
    password: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))