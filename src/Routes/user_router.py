from fastapi import APIRouter, HTTPException
from ..Models.user import *
from ..Database.db import *

user_router = APIRouter()

@user_router.post('/create')
async def create_user(user: UserCreate):
    if User.select().where(User.username == user.username).first():
        raise HTTPException(409, 'El username ya se encuentra en uso.')
    if User.select().where(User.email == user.email).first():
        raise HTTPException(409, 'El email ya existe.')
    password_hash = hash_password(user.password_hash)
    
    new_user = User.create(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth
    )

    return new_user.id


@user_router.put('/active/{id}')
async def active_user(id: str):
    user = User.select().where(User.id == int(id)).first()
    if not user:
        raise HTTPException(404, 'Usuario no encontrado.')
    user.is_active = True
    user.save()
    return user.username