from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.models.order import Order
from app.database import db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[Order])
async def list_orders():
    docs = await db['orders'].find().to_list(100)
    return docs

@router.post("/", response_model=Order)
async def create_order(order: Order):
    data = order.model_dump(by_alias=True, exclude={"id"})
    if 'items' in data:
        for item in data['items']:
            if 'item_id' in item and isinstance(item['item_id'], str):
                try:
                    item['item_id'] = ObjectId(item['item_id'])
                except InvalidId:
                    pass
    res = await db['orders'].insert_one(data)
    new_doc = await db['orders'].find_one({"_id": res.inserted_id})
    return new_doc

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