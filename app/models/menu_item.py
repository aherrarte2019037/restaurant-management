from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from bson import ObjectId
from datetime import datetime
from app.models.object_id import PyObjectId

class NutritionalInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None

class MenuItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    restaurant_id: PyObjectId
    name: str
    description: str
    price: float
    category: str
    tags: List[str] = []
    available: bool = True
    image_url: Optional[str] = None
    nutritional_info: Optional[NutritionalInfo] = None
    ingredients: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        validate_assignment = True 