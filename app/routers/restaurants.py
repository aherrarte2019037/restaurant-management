from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.models.restaurant import Restaurant
from app.database import db
from datetime import datetime

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/", response_model=List[Restaurant])
async def list_restaurants():
    restaurants_cursor = db.restaurants.find()
    restaurants_list = await restaurants_cursor.to_list(100)
    return restaurants_list

@router.post("/", response_model=Restaurant)
async def create_restaurant(restaurant: Restaurant):
    data = restaurant.model_dump(by_alias=True, exclude={"id"})

    res = await db.restaurants.insert_one(data)
    new_restaurant_doc = await db.restaurants.find_one({"_id": res.inserted_id})
    return new_restaurant_doc

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    try:
        object_id = ObjectId(restaurant_id)
        restaurant_doc = await db.restaurants.find_one({"_id": object_id})
        if not restaurant_doc:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
        return restaurant_doc
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")

@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(restaurant_id: str, restaurant: Restaurant):
    try:
        object_id = ObjectId(restaurant_id)
        data = restaurant.model_dump(by_alias=True, exclude={"id"})

        data["updated_at"] = datetime.now()
        
        res = await db.restaurants.update_one(
            {"_id": object_id}, 
            {"$set": data}
        )
        
        if res.modified_count == 0:
            existing_doc = await db.restaurants.find_one({"_id": object_id})
            if existing_doc:
                return existing_doc
            else:
                raise HTTPException(status_code=404, detail="Restaurante no encontrado para actualizar")

        updated_restaurant_doc = await db.restaurants.find_one({"_id": object_id})
        return updated_restaurant_doc
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")

@router.get("/nearby", response_model=List[Restaurant])
async def get_nearby_restaurants(lat: float, lng: float, max_distance: int = 5000):
    """Busca restaurantes cercanos a una ubicación geográfica"""
    restaurants_cursor = db.restaurants.find(
        {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat]
                    },
                    "$maxDistance": max_distance
                }
            }
        }
    )
    restaurants_list = await restaurants_cursor.to_list(100)
    return restaurants_list 