from fastapi import APIRouter
from ..Schemas.user_schema import UserCreate
from ..Services.user_service import UserService

user_router = APIRouter()

user_service = UserService(save_path_image='src/Multimedia/Image/User')

@user_router.post('/create')
async def create_user(user: UserCreate):
    return user_service.create_user(user)


@user_router.put('/active/{id}')
async def active_user(id: int):
    return user_service.active_user(id)
