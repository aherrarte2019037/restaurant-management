from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.models.restaurant import Restaurant
from app.database import db

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/", response_model=List[Restaurant])
async def list_restaurants():
    restaurants = await db.restaurants.find().to_list(100)
    return restaurants

@router.post("/", response_model=Restaurant)
async def create_restaurant(restaurant: Restaurant):
    data = restaurant.model_dump(by_alias=True, exclude={"id"})
    res = await db.restaurants.insert_one(data)
    new_restaurant = await db.restaurants.find_one({"_id": res.inserted_id})
    return new_restaurant

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    try:
        object_id = ObjectId(restaurant_id)
        restaurant = await db.restaurants.find_one({"_id": object_id})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
        return restaurant
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")

@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(restaurant_id: str, restaurant: Restaurant):
    try:
        object_id = ObjectId(restaurant_id)
        data = restaurant.model_dump(by_alias=True, exclude={"id"})
        data["updated_at"] = Restaurant.updated_at.default_factory()
        
        res = await db.restaurants.update_one(
            {"_id": object_id}, 
            {"$set": data}
        )
        
        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Restaurante no actualizado")
        
        updated_restaurant = await db.restaurants.find_one({"_id": object_id})
        return updated_restaurant
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")

@router.get("/nearby", response_model=List[Restaurant])
async def get_nearby_restaurants(lat: float, lng: float, max_distance: int = 5000):
    """Busca restaurantes cercanos a una ubicación geográfica"""
    restaurants = await db.restaurants.find(
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
    ).to_list(100)
    return restaurants 