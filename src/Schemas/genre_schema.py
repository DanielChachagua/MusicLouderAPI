from pydantic import BaseModel

class GenreRequest(BaseModel):
    name: str

class GenreDTOResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
    
# class GenreResponse(BaseModel):
#     id: int
#     name: str
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True
