from fastapi import APIRouter, Depends, Query
from ..Schemas.user_schema import UserCreate
from ..Services.user_service import UserService

user_router = APIRouter(tags=['User'])

user_service = UserService(save_path_image='src/Multimedia/Image/User')

@user_router.post('/create')
async def create_user(user: UserCreate):
    return user_service.create_user(user)


@user_router.get('/active/{token}')
async def active_user(token: str, email: str = Query(...)):
    return user_service.active_user(token, email)


