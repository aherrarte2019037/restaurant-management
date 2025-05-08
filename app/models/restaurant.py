from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

class ContactInfo(BaseModel):
    phone: str
    email: str
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "phone": "123456789",
            "email": "restaurante@ejemplo.com"
        }}
    )

class ScheduleTime(BaseModel):
    open: str
    close: str
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "open": "08:00",
            "close": "22:00"
        }}
    )

class Schedule(BaseModel):
    monday: Optional[ScheduleTime] = None
    tuesday: Optional[ScheduleTime] = None
    wednesday: Optional[ScheduleTime] = None
    thursday: Optional[ScheduleTime] = None
    friday: Optional[ScheduleTime] = None
    saturday: Optional[ScheduleTime] = None
    sunday: Optional[ScheduleTime] = None
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "monday": {"open": "08:00", "close": "22:00"},
            "tuesday": {"open": "08:00", "close": "22:00"}
        }}
    )

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]
    
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "type": "Point",
            "coordinates": [-73.9857, 40.7484]
        }}
    )

class Restaurant(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    address: str
    contact: ContactInfo
    rating: float = 0.0
    cuisine_type: List[str]
    hours: Schedule
    location: Optional[GeoLocation] = None
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
            "name": "Restaurante ABC",
            "address": "Calle Principal 123",
            "contact": {"phone": "123456789", "email": "restaurante@ejemplo.com"},
            "rating": 4.5,
            "cuisine_type": ["Italiana", "Mediterránea"],
            "hours": {
                "monday": {"open": "08:00", "close": "22:00"},
                "tuesday": {"open": "08:00", "close": "22:00"}
            }
        }}
    ) 