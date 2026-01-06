from pydantic import BaseModel


class ImageBase(BaseModel):
    name: str
    url: str


class CreateImage(ImageBase):
    pass


class Image(ImageBase):
    id: str

    class Config:
        orm_mode = True
