from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime
from app.models.object_id import PyObjectId

class CustomerBasicInfo(BaseModel):
    name: str
    email: str

class ResponseInfo(BaseModel):
    text: str
    date: datetime = Field(default_factory=datetime.now)

class Review(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    restaurant_id: PyObjectId
    order_id: Optional[PyObjectId] = None
    customer: CustomerBasicInfo
    rating: int
    comment: str
    date: datetime = Field(default_factory=datetime.now)
    helpful_votes: int = 0
    response: Optional[ResponseInfo] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        validate_assignment = True 