from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

class NutritionalInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "calories": 450.0,
            "protein": 20.0,
            "carbs": 30.0,
            "fat": 15.0
        }}
    )

class MenuItem(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    restaurant_id: str
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
    
    @model_validator(mode='before')
    @classmethod
    def convert_objectid_to_str(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if '_id' in data and isinstance(data['_id'], ObjectId):
                data['_id'] = str(data['_id'])
        return data
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={"example": {
            "restaurant_id": "5f8d0f3e9c9d1c2a3b4c5d6f",
            "name": "Hamburguesa Clásica",
            "description": "Deliciosa hamburguesa de carne con lechuga, tomate y queso",
            "price": 10.99,
            "category": "Hamburguesas",
            "tags": ["Carne", "Clásico"],
            "available": True,
            "ingredients": ["Carne", "Pan", "Lechuga", "Tomate", "Queso"]
        }}
    ) 