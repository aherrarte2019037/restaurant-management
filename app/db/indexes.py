from motor.motor_asyncio import AsyncIOMotorClient
from app.database import db

async def create_indexes():
    """Crea los índices necesarios para todas las colecciones"""
    
    # Índices para restaurants
    await db.restaurants.create_index("name")
    await db.restaurants.create_index("cuisine_type")
    await db.restaurants.create_index([("location", "2dsphere")])
    await db.restaurants.create_index([("rating", -1)])
    
    # Índices para menu_items
    await db.menu_items.create_index("restaurant_id")
    await db.menu_items.create_index([("restaurant_id", 1), ("category", 1)])
    await db.menu_items.create_index("tags")
    await db.menu_items.create_index("price")
    await db.menu_items.create_index([("name", "text"), ("description", "text")])
    
    # Índices para orders
    await db.orders.create_index("order_id", unique=True)
    await db.orders.create_index("restaurant")
    await db.orders.create_index("customer.email")
    await db.orders.create_index([("date", -1)])
    await db.orders.create_index("status")
    await db.orders.create_index([("restaurant", 1), ("date", -1)])
    
    # Índices para reviews
    await db.reviews.create_index("restaurant_id")
    await db.reviews.create_index("order_id")
    await db.reviews.create_index("customer.email")
    await db.reviews.create_index([("rating", -1)])
    await db.reviews.create_index([("date", -1)])
    await db.reviews.create_index([("comment", "text")])
    
    print("✅ Índices creados correctamente") 