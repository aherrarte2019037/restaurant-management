from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.menu_item import MenuItem
from app.database import db
from datetime import datetime
import motor.motor_asyncio # Importar motor para GridFS
from starlette.responses import StreamingResponse

# Crear instancia de GridFS
fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

@router.get("/", response_model=List[MenuItem])
async def list_menu_items(restaurant_id: Optional[str] = None, category: Optional[str] = None):
    """Listar todos los elementos del menú, opcionalmente filtrados por restaurante y/o categoría"""
    query = {}
    
    if restaurant_id:
        try:
            query["restaurant_id"] = ObjectId(restaurant_id)
        except InvalidId:
            return []
    
    if category:
        query["category"] = category
    
    menu_items_list = await db.menu_items.find(query, {"nutritional_info": 0}).to_list(100) # Excluir nutritional_info (proyección)
    return menu_items_list

@router.post("/", response_model=MenuItem)
async def create_menu_item(menu_item: MenuItem):
    """Crear un nuevo elemento del menú"""
    data = menu_item.model_dump(by_alias=True, exclude={"id"})
    if 'restaurant_id' in data and isinstance(data['restaurant_id'], str):
        try:
            data['restaurant_id'] = ObjectId(data['restaurant_id'])
        except InvalidId:
             raise HTTPException(status_code=400, detail="ID de restaurante inválido en el cuerpo de la solicitud")
             
    res = await db.menu_items.insert_one(data)
    new_menu_item_doc = await db.menu_items.find_one({"_id": res.inserted_id})
    return new_menu_item_doc

@router.get("/{item_id}", response_model=MenuItem)
async def get_menu_item(item_id: str):
    """Obtener un elemento específico del menú por ID"""
    try:
        object_id = ObjectId(item_id)
        menu_item_doc = await db.menu_items.find_one({"_id": object_id})
        if not menu_item_doc:
            raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")
        return menu_item_doc
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de elemento del menú inválido")

@router.put("/{item_id}", response_model=MenuItem)
async def update_menu_item(item_id: str, menu_item: MenuItem):
    """Actualizar un elemento del menú"""
    try:
        object_id = ObjectId(item_id)
        data = menu_item.model_dump(by_alias=True, exclude={"id"})
        if 'restaurant_id' in data and isinstance(data['restaurant_id'], str):
             try:
                 data['restaurant_id'] = ObjectId(data['restaurant_id'])
             except InvalidId:
                 raise HTTPException(status_code=400, detail="ID de restaurante inválido en el cuerpo de la solicitud")
                 
        data["updated_at"] = datetime.now()
        
        res = await db.menu_items.update_one(
            {"_id": object_id}, 
            {"$set": data}
        )
        
        if res.modified_count == 0:
            existing_doc = await db.menu_items.find_one({"_id": object_id})
            if existing_doc:
                 return existing_doc
            else:
                 raise HTTPException(status_code=404, detail="Elemento del menú no actualizado o no encontrado")

        updated_menu_item_doc = await db.menu_items.find_one({"_id": object_id})
        return updated_menu_item_doc
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de elemento del menú inválido")

@router.delete("/{item_id}")
async def delete_menu_item(item_id: str):
    """Eliminar un elemento del menú"""
    try:
        object_id = ObjectId(item_id)
        res = await db.menu_items.delete_one({"_id": object_id})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")
        return {"status": "eliminado"}
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de elemento del menú inválido")

@router.get("/search/", response_model=List[MenuItem])
async def search_menu_items(query: str):
    """Buscar elementos del menú por nombre o descripción"""
    menu_items_list = await db.menu_items.find(
        {"$text": {"$search": query}}
    ).to_list(100)
    return menu_items_list

@router.post("/{item_id}/image", status_code=201)
async def upload_menu_item_image(item_id: str, file: UploadFile = File(...)):
    """Sube una imagen para un elemento del menú específico."""
    try:
        object_id = ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de elemento del menú inválido")

    # Verificar si el item existe
    menu_item = await db.menu_items.find_one({"_id": object_id})
    if not menu_item:
        raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")

    # Subir archivo a GridFS
    try:
        grid_id = await fs.upload_from_stream(
            file.filename,
            file.file, # El objeto archivo/stream
            metadata={"content_type": file.content_type} # Guardar content type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo: {e}")

    # Actualizar el menu item con el ID de la imagen de GridFS
    await db.menu_items.update_one(
        {"_id": object_id},
        {"$set": {"image_id": str(grid_id), "updated_at": datetime.now()}}
    )

    return {"filename": file.filename, "image_id": str(grid_id)}

@router.get("/{item_id}/image")
async def get_menu_item_image(item_id: str):
    """Obtiene la imagen de un elemento del menú específico."""
    try:
        object_id = ObjectId(item_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de elemento del menú inválido")

    menu_item = await db.menu_items.find_one({"_id": object_id})
    if not menu_item:
        raise HTTPException(status_code=404, detail="Elemento del menú no encontrado")

    image_id_str = menu_item.get("image_id")
    if not image_id_str:
        raise HTTPException(status_code=404, detail="Imagen no encontrada para este elemento")

    try:
        image_object_id = ObjectId(image_id_str)
    except InvalidId:
        # Esto no debería pasar si guardamos strings válidos, pero por seguridad
        raise HTTPException(status_code=500, detail="ID de imagen almacenado inválido") 

    try:
        grid_out = await fs.open_download_stream(image_object_id)
        content_type = grid_out.metadata.get("content_type", "application/octet-stream")
        # Devolver el stream del archivo
        return StreamingResponse(grid_out, media_type=content_type)
    except Exception as e: # Podría ser NoFile si el ID no está en GridFS
        print(f"Error buscando imagen en GridFS {image_id_str}: {e}")
        raise HTTPException(status_code=404, detail="Archivo de imagen no encontrado en GridFS") 