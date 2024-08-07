from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from decouple import config
from ..Schemas.user_schema import UserInfo
from ..Models.user_model import User

auth_router = APIRouter()

oauth_scheme = OAuth2PasswordBearer('/token')

@auth_router.post('/auth')
async def auth(data: OAuth2PasswordRequestForm = Depends()):
    user = User.authenticate(data.username, data.password)
    print(user)
    if user:
        return UserInfo.model_validate(user)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Credenciales incorrectas', headers={ 'WWW-Authenticate' : 'Bearer'})

def create_token(user, hours=2):
    data = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=hours)
    }
    encoded_jwt = jwt.encode(data, config('SECRET_KEY'), algorithm="HS256")
    return encoded_jwt

def decode_token(token):
    try:
        return jwt.decode(token, config('SECRET_KEY'), algorithms=["HS256"])
    except Exception as e:
        return None

def get_current_user(token: str = Depends(oauth_scheme)):
    data = decode_token(token)
    if data:
        return User.get_by_id(data['user_id'])
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access Token no valido', headers={ 'WWW-Authenticate' : 'Bearer'})

@auth_router.post('/token')
async def login():
    return 'login'