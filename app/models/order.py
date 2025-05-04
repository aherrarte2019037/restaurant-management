from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from bson import ObjectId
from datetime import datetime

class OrderItem(BaseModel):
    item_id: str = Field(default=None)
    name: str
    price: float
    quantity: int
    special_instructions: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "item_id": "5f8d0f3e9c9d1c2a3b4c5d6e",
            "name": "Hamburguesa",
            "price": 10.99,
            "quantity": 2,
            "special_instructions": "Sin cebolla"
        }}
    )

class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "name": "Juan Pérez",
            "email": "juan@ejemplo.com",
            "phone": "123456789",
            "address": "Calle Principal 123"
        }}
    )

class Order(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
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
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={"example": {
            "_id": "5f8d0f3e9c9d1c2a3b4c5d6e",
            "order_id": 12345,
            "restaurant": "Restaurante ABC",
            "date": "2023-01-01T12:00:00",
            "customer": {"name": "Juan Pérez", "email": "juan@ejemplo.com"},
            "items": [{"name": "Hamburguesa", "price": 10.99, "quantity": 2}],
            "total_amount": 21.98,
            "status": "pendiente",
            "payment_status": "pendiente"
        }}
    ) 