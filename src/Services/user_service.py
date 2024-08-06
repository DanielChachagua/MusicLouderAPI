from fastapi import APIRouter, HTTPException
from ..Schemas.user_schema import *
from ..Database.db import *


user_router = APIRouter()

class UserService:
    def __init__(self, save_path_image: str):
        self.save_path_image = save_path_image

    def create_user(self, user: UserCreate):
        if User.select().where(User.username == user.username).first():
            raise HTTPException(409, 'El username ya se encuentra en uso.')
        if User.select().where(User.email == user.email).first():
            raise HTTPException(409, 'El email ya existe.')

        new_user = User.create(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            date_of_birth=user.date_of_birth
        )
        return new_user.id
    

    def active_user(self, id: int):
        user = User.select().where(User.id == id).first()
        if not user:
            raise HTTPException(404, 'Usuario no encontrado.')
        user.is_active = True
        user.save()
        return user.username
    
    def check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    