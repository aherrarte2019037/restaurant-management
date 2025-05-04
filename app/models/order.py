from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from datetime import datetime
from app.models.object_id import PyObjectId

class OrderItem(BaseModel):
    item_id: PyObjectId = Field(default_factory=PyObjectId)
    name: str
    price: float
    quantity: int
    special_instructions: Optional[str] = None

class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    order_id: int
    restaurant: str
    date: datetime = Field(default_factory=datetime.now)
    customer: CustomerInfo
    items: List[OrderItem]
    total_amount: float
    status: str = "pendiente"
    payment_method: Optional[str] = None
    payment_status: str = "pendiente"
    delivery_time: Optional[datetime] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        validate_assignment = True 