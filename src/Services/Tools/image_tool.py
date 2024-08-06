import os
import uuid
from PIL import Image
from fastapi import HTTPException, UploadFile

class ImageTool:
    MAX_FILE_SIZE = 2 * 1024 * 1024  #2 MB
    ALLOWED_MIME_TYPES = [
        "image/jpeg",
        "image/png",
    ]
    mime_to_extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }

    def __init__(self, path_image: str) -> None:
        self.path_image = path_image
        os.makedirs(self.path_image, exist_ok=True)

    def reset_name_image(self, filename: str) -> str:
        nombre, extension = os.path.splitext(filename)
        nuevo_nombre = f"{uuid.uuid4()}{extension}"
        return nuevo_nombre

    def save_image(self, image_file: UploadFile, dimension: tuple) -> str:
        if 'image' not in image_file.content_type:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Los formatos válidos son: JPEG, PNG")
        file_size = len(image_file.file.read())
        image_file.file.seek(0)  # Reset the file pointer to the beginning after reading size

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="La imagen no puede exceder los 2MB")

        file_extension = self.mime_to_extension[image_file.content_type]
        filename = self.reset_name_image(f"{uuid.uuid4().hex}{file_extension}")
        file_location = os.path.join(self.path_image, filename)

        try:
            image = Image.open(image_file.file)
            image.thumbnail(dimension)
            image.save(file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")
        
        return filename
    # async def save_image(self, image_file: UploadFile, dimension: tuple) -> str:
    #     if image_file.content_type not in self.ALLOWED_MIME_TYPES:
    #         raise HTTPException(status_code=400, detail="Formato de imagen no soportado. Los formatos válidos son: JPEG, PNG")

    #     file_size = len(await image_file.read())
    #     await image_file.seek(0)  # Reset the file pointer to the beginning after reading size

    #     if file_size > self.MAX_FILE_SIZE:
    #         raise HTTPException(status_code=413, detail="La imagen no puede exceder los 2MB")

    #     file_extension = self.mime_to_extension.get(image_file.content_type, "")
    #     filename = self.reset_name_image(f"{uuid.uuid4().hex}{file_extension}")
    #     file_location = os.path.join(self.path_image, filename)

    #     try:
    #         image = Image.open(image_file.file)
    #         image.thumbnail(dimension)
    #         image.save(file_location)
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Error al guardar la imagen: {str(e)}")
        
    #     return filename

    def delete_image(self, filename: str) -> None:
        media_path = os.path.join(self.path_image, filename)
        if os.path.exists(media_path):
            os.remove(media_path)
        else:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
