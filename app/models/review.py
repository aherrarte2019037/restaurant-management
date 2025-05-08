from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Any
from bson import ObjectId
from datetime import datetime

class CustomerBasicInfo(BaseModel):
    name: str
    email: str
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "name": "Juan Pérez",
            "email": "juan@ejemplo.com"
        }}
    )

class ResponseInfo(BaseModel):
    text: str
    date: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "text": "Gracias por su reseña. Lamentamos los inconvenientes.",
            "date": "2023-01-02T15:30:00"
        }}
    )

class Review(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    restaurant_id: str
    order_id: Optional[str] = None
    customer: CustomerBasicInfo
    rating: int
    comment: str
    date: datetime = Field(default_factory=datetime.now)
    helpful_votes: int = 0
    response: Optional[ResponseInfo] = None
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
            "_id": "5f8d0f3e9c9d1c2a3b4c5d6e",
            "restaurant_id": "5f8d0f3e9c9d1c2a3b4c5d6f",
            "order_id": "5f8d0f3e9c9d1c2a3b4c5d7a",
            "customer": {"name": "Juan Pérez", "email": "juan@ejemplo.com"},
            "rating": 4,
            "comment": "Muy buen servicio y comida deliciosa",
            "date": "2023-01-01T18:30:00",
            "helpful_votes": 5
        }}
    ) 