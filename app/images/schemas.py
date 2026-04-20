from pydantic import BaseModel


class ImageBase(BaseModel):
    name: str
    url: str


class CreateImage(ImageBase):
    pass


class Image(ImageBase):
    id: str

    class Config:
        from_attributes = True
