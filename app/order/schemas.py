from typing import List
from pydantic import BaseModel, validator


class CreateOrder(BaseModel):
    name: str
    delivery_type: str
    city: str
    department_number: str
    phone_number: str
    privacy_policy_accepted: bool

    @validator("privacy_policy_accepted")
    def must_accept_privacy_policy(cls, v):
        if not v:
            raise ValueError("Необхідно надати згоду на обробку персональних даних")
        return v

    class Config:
        validate_assignment = True


class DeliveryType(BaseModel):
    delivery_types: List[str] = ["Нова Пошта", "Укрпошта"]