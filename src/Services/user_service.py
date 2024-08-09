from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from ..Schemas.user_schema import *
from ..Database.db import *
from .Tools.email_tool import MailTool
from decouple import config


user_router = APIRouter()

class UserService:
    def __init__(self, save_path_image: str):
        self.save_path_image = save_path_image

    def create_user(self, user: UserCreate):
        if User.select().where(User.username == user.username).first():
            raise HTTPException(409, 'El username ya se encuentra en uso.')
        if User.select().where(User.email == user.email).first():
            raise HTTPException(409, 'El email ya existe.')

        new_user: User = User.create(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            date_of_birth=user.date_of_birth
        )

        mail = MailTool(
            smtp_server=config('EMAIL_HOST'), 
            port=config('EMAIL_PORT'),
            username=config('EMAIL_HOST_USER'),
            password=config('EMAIL_HOST_PASSWORD')    
        )

        mail.send_email(
            subject='Bienvenido a MusicLouder',
            body=f'''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>
                </head>
                <body>
                    <div style="display: block; justify-content: center; align-items: start; gap: 20px;">
                        <h1>Bienvenido, {new_user.username}</h1>
                        <p>Hola {new_user.last_name}, {new_user.first_name} , Bienvenido a MusicLouder, una aplicacion mas de empresas Byte-Force.</p>
                        <p>Al registrarse podra contar con diferentes beneficios, como crear canciones, albumes, artistas y tu propiaplaylist.</p>
                        <h4>Disfruta de la aplicacion!!!</h4>
                        <h3><strong>Por favor no se olvide de activar su cuenta con el boton de confirmacion</strong></h3>
                        <a href="http://localhost:8000/user/active/{new_user.token}?email={new_user.email}"><h2>Confirmar Cuenta</h2></a>
                    </div>
                </body>
                </html>
            ''',
                        #<a href="https://ml-back.pablocamacho.com.ar/user/activate/{user.password_hash}?email={user.email}"><h2>Confirmar Cuenta</h2></a>
            to_email=user.email
        )

        return new_user.id
    

    def active_user(self, token: str, email: str):
        print(token)
        print(email)
        user: User = User.select().where(User.token == token).first()
        
        if not user:
            raise HTTPException(404, 'Usuario no encontrado.')
        
        if user.email == email:
            user.is_active = True
            user.save()
            
            # Redirigir a otra página
            return RedirectResponse(url="https://ml-back.pablocamacho.com.ar/docs/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error al validar usuario')
    

    
    
    