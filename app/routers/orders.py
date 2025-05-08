from fastapi import APIRouter, HTTPException, Body, status, Query
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from app.models.order import Order, PaginatedOrders
from app.database import db
from datetime import datetime
import pymongo

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=PaginatedOrders)
async def list_orders(
    restaurant_id: Optional[str] = None,
    customer_email: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = 'date',
    sort_order: int = -1,
    skip: int = 0,
    limit: int = 20
):
    """Lista pedidos con filtros, paginación y ordenamiento."""
    query = {}
    if restaurant_id:
        try:
            query["restaurant_id"] = ObjectId(restaurant_id)
        except InvalidId:
            return {"total": 0, "orders": []}
    if customer_email:
        query["customer.email"] = {"$regex": customer_email, "$options": "i"}
    if status:
        query["status"] = status
    
    if sort_order not in [-1, 1]:
        sort_order = -1
        
    allowed_sort_fields = ['date', 'total_amount', 'status', 'customer.name', 'restaurant_id'] 
    if sort_by not in allowed_sort_fields:
        sort_by = 'date'
        
    sort_query = [(sort_by, sort_order)]
    
    try:
        total_count = await db['orders'].count_documents(query)
        
        cursor = db['orders'].find(query).sort(sort_query).skip(skip).limit(limit)
        docs = await cursor.to_list(limit)
        
        return {"total": total_count, "orders": docs}
        
    except Exception as e:
        print(f"Error en list_orders: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los pedidos")

@router.post("/", response_model=Order)
async def create_order(order: Order):
    data = order.model_dump(by_alias=True, exclude={"id"})
    try:
        if 'restaurant_id' in data and isinstance(data['restaurant_id'], str):
             data['restaurant_id'] = ObjectId(data['restaurant_id'])
        if 'items' in data:
            for item in data['items']:
                if 'item_id' in item and isinstance(item['item_id'], str):
                    try:
                        item['item_id'] = ObjectId(item['item_id'])
                    except InvalidId:
                        pass 
    except InvalidId:
         raise HTTPException(status_code=400, detail="ID de restaurante o item inválido en el cuerpo")
                         
    res = await db['orders'].insert_one(data)
    new_doc = await db['orders'].find_one({"_id": res.inserted_id})
    return new_doc

@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_orders_batch(orders: List[Order]):
    print(orders)

    """Crea múltiples pedidos en un solo lote."""
    if not orders:
        raise HTTPException(status_code=400, detail="La lista de pedidos no puede estar vacía.")
        
    orders_to_insert = []
    errors = []
    
    for i, order in enumerate(orders):
        try:
            # El modelo ya valida que 'restaurant' es un string
            data = order.model_dump(by_alias=True, exclude={"id"}) 
            
            # Convertir el ID del restaurante (que viene en el campo 'restaurant') a ObjectId
            # y guardarlo como 'restaurant_id' para MongoDB (o mantener 'restaurant' si prefieres)
            if 'restaurant' in data and isinstance(data['restaurant'], str):
                data['restaurant_id'] = ObjectId(data['restaurant']) # Crear nuevo campo para DB
                # Opcional: eliminar el campo string original si no lo quieres en la DB
                # del data['restaurant'] 
            else:
                # Si el campo 'restaurant' falta o no es string, Pydantic ya debería haber fallado
                # Pero añadimos un error por si acaso
                errors.append(f"Error en Pedido #{i+1}: Campo 'restaurant' inválido o faltante.")
                continue # Saltar este pedido
            
            # Convertir IDs de items si vienen como str
            if 'items' in data:
                for item in data['items']:
                     if 'item_id' in item and isinstance(item['item_id'], str):
                         item['item_id'] = ObjectId(item['item_id'])
            
            # Añadir timestamps
            data.setdefault("created_at", datetime.now())
            data.setdefault("updated_at", datetime.now())
                         
            orders_to_insert.append(data)
        except InvalidId:
            errors.append(f"Error en Pedido #{i+1}: ID de Restaurante o Item inválido.")
        except Exception as e:
            errors.append(f"Error procesando Pedido #{i+1}: {e}")
            
    if errors:
         raise HTTPException(status_code=400, detail={"errors": errors, "message": "No se pudieron procesar todos los pedidos."}) 
         
    if not orders_to_insert:
         raise HTTPException(status_code=400, detail="No hay pedidos válidos para insertar.")

    try:
        result = await db['orders'].insert_many(orders_to_insert)
        # Devolver algo más útil que solo el conteo podría ser bueno
        # return {"created_count": len(result.inserted_ids), "inserted_ids": [str(id) for id in result.inserted_ids]}
        return {"created_count": len(result.inserted_ids)} # Mantener simple por ahora
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar pedidos en la base de datos: {e}")

@router.get("/{oid}", response_model=Order)
async def get_order(oid: str):
    try:
        object_id = ObjectId(oid)
        doc = await db['orders'].find_one({"_id": object_id})
        if not doc:
            raise HTTPException(404, "Pedido no encontrado")
        return doc
    except InvalidId:
        raise HTTPException(404, "ID de pedido inválido")

@router.put("/{oid}", response_model=Order)
async def update_order(oid: str, order: Order):
    try:
        object_id = ObjectId(oid)
        data = order.model_dump(by_alias=True, exclude={"id"})
        if 'items' in data:
            for item in data['items']:
                if 'item_id' in item and isinstance(item['item_id'], str):
                    try:
                        item['item_id'] = ObjectId(item['item_id'])
                    except InvalidId:
                        pass
        data["updated_at"] = datetime.now()
        res = await db['orders'].update_one({"_id": object_id}, {"$set": data})
        if res.modified_count == 0:
            existing_doc = await db['orders'].find_one({"_id": object_id})
            if existing_doc:
                return existing_doc
            else:
                raise HTTPException(404, "Pedido no actualizado o no encontrado")
        
        updated_doc = await db['orders'].find_one({"_id": object_id})
        return updated_doc
    except InvalidId:
        raise HTTPException(404, "ID de pedido inválido")

@router.patch("/{oid}/status", response_model=Order)
async def update_order_status(oid: str, status_update: dict = Body(...)):
    """Actualiza solo el estado de un pedido."""
    new_status = status_update.get('status')
    if not new_status:
        raise HTTPException(status_code=400, detail="El campo 'status' es requerido en el body.")
        
    # Aquí podrías añadir validación extra para asegurarte que new_status sea válido
    allowed_statuses = ['pendiente', 'en_proceso', 'listo_para_recoger', 'en_camino', 'entregado', 'cancelado']
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Estado '{new_status}' inválido.")
        
    try:
        object_id = ObjectId(oid)
        update_data = {
            "$set": {
                "status": new_status,
                "updated_at": datetime.now()
            }
        }
        res = await db['orders'].update_one({"_id": object_id}, update_data)
        
        if res.modified_count == 0:
            existing_doc = await db['orders'].find_one({"_id": object_id})
            if existing_doc:
                 return existing_doc # Devolver sin cambios si no se modificó o ya tenía ese estado
            else:
                 raise HTTPException(status_code=404, detail="Pedido no encontrado para actualizar estado")

        updated_doc = await db['orders'].find_one({"_id": object_id})
        return updated_doc
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

@router.delete("/{oid}")
async def delete_order(oid: str):
    try:
        object_id = ObjectId(oid)
        res = await db['orders'].delete_one({"_id": object_id})
        if res.deleted_count == 0:
            raise HTTPException(404, "Pedido no encontrado")
        return {"status": "eliminado"}
    except InvalidId:
        raise HTTPException(404, "ID de pedido inválido") 