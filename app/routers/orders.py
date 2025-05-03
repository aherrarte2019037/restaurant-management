from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from app.models.order import Order
from app.database import db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[Order])
def list_orders():
    docs = list(db['orders'].find())
    return docs

@router.post("/", response_model=Order)
def create_order(order: Order):
    data = order.dict(by_alias=True, exclude={"id"})
    res = db['orders'].insert_one(data)
    new_doc = db['orders'].find_one({"_id": res.inserted_id})
    return new_doc

@router.get("/{oid}", response_model=Order)
def get_order(oid: str):
    doc = db['orders'].find_one({"_id": ObjectId(oid)})
    if not doc:
        raise HTTPException(404, "Pedido no encontrado")
    return doc

@router.put("/{oid}", response_model=Order)
def update_order(oid: str, order: Order):
    data = order.dict(by_alias=True, exclude={"id"})
    res = db['orders'].update_one({"_id": ObjectId(oid)}, {"$set": data})
    if res.modified_count == 0:
        raise HTTPException(404, "Pedido no actualizado")
    return db['orders'].find_one({"_id": ObjectId(oid)})

@router.delete("/{oid}")
def delete_order(oid: str):
    res = db['orders'].delete_one({"_id": ObjectId(oid)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Pedido no encontrado")
    return {"status": "eliminado"} 