from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from app.models.object_id import PyObjectId

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    order_id: int
    restaurant: str
    date: str
    total_amount: float
    rating: int
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True  # Updated from allow_population_by_field_name 