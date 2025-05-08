from fastapi import APIRouter, HTTPException, Body, status
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.restaurant import Restaurant
from app.database import db
from datetime import datetime
import pymongo
from pydantic import BaseModel

class CuisineTypePayload(BaseModel):
    type: str

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

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(restaurant_id: str):
    """Elimina un restaurante por ID."""
    try:
        object_id = ObjectId(restaurant_id)
        res = await db.restaurants.delete_one({"_id": object_id})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
        return None
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")

@router.post("/{restaurant_id}/cuisine-types", response_model=Restaurant, status_code=status.HTTP_200_OK)
async def add_cuisine_type(restaurant_id: str, payload: CuisineTypePayload):
    """Manejo de arrays"""
    """Añade un tipo de cocina a la lista de un restaurante (si no existe)."""
    try:
        object_id = ObjectId(restaurant_id)
        cuisine_type_to_add = payload.type.strip() # Limpiar espacios
        if not cuisine_type_to_add:
            raise HTTPException(status_code=400, detail="El tipo de cocina no puede estar vacío.")
            
        # Usar $addToSet para añadir sin duplicados
        result = await db.restaurants.update_one(
            {"_id": object_id},
            {
                "$addToSet": {"cuisine_type": cuisine_type_to_add},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        updated_restaurant = await db.restaurants.find_one({"_id": object_id})
        return updated_restaurant
        
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")
    except Exception as e:
        print(f"Error añadiendo tipo de cocina: {e}")
        raise HTTPException(status_code=500, detail="Error interno añadiendo tipo de cocina")

@router.delete("/{restaurant_id}/cuisine-types/{type_name}", response_model=Restaurant, status_code=status.HTTP_200_OK)
async def remove_cuisine_type(restaurant_id: str, type_name: str):
    """Manejo de arrays"""
    """Elimina un tipo de cocina de la lista de un restaurante."""
    try:
        object_id = ObjectId(restaurant_id)
        type_to_remove = type_name.strip()
        
        # Usar $pull para eliminar el elemento del array
        result = await db.restaurants.update_one(
            {"_id": object_id},
            {
                "$pull": {"cuisine_type": type_to_remove},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        if result.matched_count == 0:
             raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        updated_restaurant = await db.restaurants.find_one({"_id": object_id})
        if not updated_restaurant:
             raise HTTPException(status_code=404, detail="Restaurante no encontrado después de eliminar tipo") 
        return updated_restaurant
        
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")
    except Exception as e:
        print(f"Error eliminando tipo de cocina: {e}")
        raise HTTPException(status_code=500, detail="Error interno eliminando tipo de cocina") 