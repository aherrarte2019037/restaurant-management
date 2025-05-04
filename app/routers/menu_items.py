from fastapi import APIRouter, HTTPException
from typing import List, Optional
from bson import ObjectId
from app.models.menu_item import MenuItem
from app.database import db

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

@router.get("/", response_model=List[MenuItem])
async def list_menu_items(restaurant_id: Optional[str] = None, category: Optional[str] = None):
    """Listar todos los elementos del menú, opcionalmente filtrados por restaurante y/o categoría"""
    query = {}
    
    if restaurant_id:
        query["restaurant_id"] = ObjectId(restaurant_id)
    
    if category:
        query["category"] = category
    
    menu_items = await db.menu_items.find(query).to_list(100)
    return menu_items

@router.post("/", response_model=MenuItem)
async def create_menu_item(menu_item: MenuItem):
    """Crear un nuevo elemento del menú"""
    data = menu_item.dict(by_alias=True, exclude={"id"})
    res = await db.menu_items.insert_one(data)
    new_menu_item = await db.menu_items.find_one({"_id": res.inserted_id})
    return new_menu_item

@router.get("/{item_id}", response_model=MenuItem)
async def get_menu_item(item_id: str):
    """Obtener un elemento específico del menú por ID"""
    menu_item = await db.menu_items.find_one({"_id": ObjectId(item_id)})
    if not menu_item:
        raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")
    return menu_item

@router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(item_id: str, menu_item: MenuItem):
    """Actualizar un elemento del menú"""
    data = menu_item.dict(by_alias=True, exclude={"id"})
    data["updated_at"] = MenuItem.updated_at.default_factory()
    
    res = await db.menu_items.update_one(
        {"_id": ObjectId(item_id)}, 
        {"$set": data}
    )
    
    if res.modified_count == 0:
        raise HTTPException(status_code=404, detail="Elemento del menú no actualizado")
    
    updated_menu_item = await db.menu_items.find_one({"_id": ObjectId(item_id)})
    return updated_menu_item

@router.delete("/{item_id}")
async def delete_menu_item(item_id: str):
    """Eliminar un elemento del menú"""
    res = await db.menu_items.delete_one({"_id": ObjectId(item_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")
    return {"status": "eliminado"}

@router.get("/search/", response_model=List[MenuItem])
async def search_menu_items(query: str):
    """Buscar elementos del menú por nombre o descripción"""
    menu_items = await db.menu_items.find(
        {"$text": {"$search": query}}
    ).to_list(100)
    return menu_items 