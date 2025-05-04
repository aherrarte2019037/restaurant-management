from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from bson import ObjectId
from datetime import datetime
from app.models.object_id import PyObjectId

class ContactInfo(BaseModel):
    phone: str
    email: str

class ScheduleTime(BaseModel):
    open: str
    close: str

class Schedule(BaseModel):
    monday: Optional[ScheduleTime] = None
    tuesday: Optional[ScheduleTime] = None
    wednesday: Optional[ScheduleTime] = None
    thursday: Optional[ScheduleTime] = None
    friday: Optional[ScheduleTime] = None
    saturday: Optional[ScheduleTime] = None
    sunday: Optional[ScheduleTime] = None

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class Restaurant(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    address: str
    contact: ContactInfo
    rating: float = 0.0
    cuisine_type: List[str]
    hours: Schedule
    location: Optional[GeoLocation] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {ObjectId: str}
        validate_by_name = True
        validate_assignment = True 