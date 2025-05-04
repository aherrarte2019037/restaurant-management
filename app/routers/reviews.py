from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.review import Review, ResponseInfo
from app.database import db

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("/", response_model=List[Review])
async def list_reviews(restaurant_id: Optional[str] = None):
    """Listar todas las reseñas, opcionalmente filtradas por restaurante"""
    query = {}
    
    if restaurant_id:
        try:
            query["restaurant_id"] = ObjectId(restaurant_id)
        except InvalidId:
            return []
    
    reviews = await db.reviews.find(query).sort("date", -1).to_list(100)
    return reviews

@router.post("/", response_model=Review)
async def create_review(review: Review):
    """Crear una nueva reseña"""
    data = review.model_dump(by_alias=True, exclude={"id"})
    
    # Actualizar el rating del restaurante
    restaurant_id = data["restaurant_id"]
    
    res = await db.reviews.insert_one(data)
    new_review = await db.reviews.find_one({"_id": res.inserted_id})
    
    # Calcular el nuevo rating promedio para el restaurante
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {"_id": None, "average": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    
    result = await db.reviews.aggregate(pipeline).to_list(1)
    
    if result:
        avg_rating = result[0]["average"]
        # Actualizar el rating en el restaurante
        await db.restaurants.update_one(
            {"_id": restaurant_id},
            {"$set": {"rating": round(avg_rating, 1), "updated_at": Review.updated_at.default_factory()}}
        )
    
    return new_review

@router.get("/{review_id}", response_model=Review)
async def get_review(review_id: str):
    """Obtener una reseña específica por ID"""
    try:
        object_id = ObjectId(review_id)
        review = await db.reviews.find_one({"_id": object_id})
        if not review:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return review
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de reseña inválido")

@router.put("/{review_id}/response", response_model=Review)
async def add_response(review_id: str, response: ResponseInfo):
    """Añadir una respuesta a una reseña"""
    try:
        object_id = ObjectId(review_id)
        data = response.model_dump()
        data["date"] = response.date
        
        res = await db.reviews.update_one(
            {"_id": object_id},
            {"$set": {
                "response": data,
                "updated_at": Review.updated_at.default_factory()
            }}
        )
        
        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada o no actualizada")
        
        updated_review = await db.reviews.find_one({"_id": object_id})
        return updated_review
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de reseña inválido")

@router.put("/{review_id}/helpful", response_model=Review)
async def mark_helpful(review_id: str):
    """Incrementar el contador de votos útiles para una reseña"""
    try:
        object_id = ObjectId(review_id)
        res = await db.reviews.update_one(
            {"_id": object_id},
            {"$inc": {"helpful_votes": 1}}
        )
        
        if res.modified_count == 0:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        
        updated_review = await db.reviews.find_one({"_id": object_id})
        return updated_review
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de reseña inválido") 