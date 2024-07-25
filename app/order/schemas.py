from typing import List
from pydantic import BaseModel
from datetime import datetime


class CreateOrder(BaseModel):
    name: str
    delivery_type: str
    city: str
    department_number: str
    phone_number: str


    class Config:
        validate_assignment = True


class DeliveryType(BaseModel):
    delivery_types: List[str] = ["Нова Пошта", "Укрпошта"]


