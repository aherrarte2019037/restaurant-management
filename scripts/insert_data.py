import os
import sys
import asyncio
from pathlib import Path
from faker import Faker
from bson import ObjectId
from random import choice, randint, uniform, sample
from datetime import datetime, timedelta
import uuid

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

try:
    from app.database import db
    from app.models.restaurant import Restaurant, ContactInfo, Schedule, ScheduleTime, GeoLocation
    from app.models.menu_item import MenuItem, NutritionalInfo
    from app.models.order import Order, OrderItem, CustomerInfo
    from app.models.review import Review, CustomerBasicInfo, ResponseInfo
except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print("Asegúrate de que estás ejecutando este script desde el directorio raíz del proyecto o que el PYTHONPATH está configurado correctamente.")
    sys.exit(1)

fake = Faker('es_ES')

def create_fake_contact_info():
    return ContactInfo(
        phone=fake.phone_number(),
        email=fake.company_email()
    )

def create_fake_schedule_time():
    open_hour = randint(8, 12)
    close_hour = randint(18, 23)
    return ScheduleTime(
        open=f"{open_hour:02d}:00",
        close=f"{close_hour:02d}:00"
    )

def create_fake_schedule():
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    schedule = {day: create_fake_schedule_time() if uniform(0, 1) > 0.1 else None for day in days}
    if all(v is None for v in schedule.values()):
        schedule['friday'] = create_fake_schedule_time()
        schedule['saturday'] = create_fake_schedule_time()
    return Schedule(**schedule)

def create_fake_geolocation():
    return GeoLocation(
        coordinates=[float(fake.longitude()), float(fake.latitude())]
    )

def create_fake_restaurant(num_restaurants=10):
    restaurants = []
    cuisine_types = ['Italiana', 'Mexicana', 'China', 'Japonesa', 'India', 'Mediterránea', 'Americana', 'Española', 'Francesa', 'Tailandesa']
    for _ in range(num_restaurants):
        restaurant_data = {
            "name": fake.company() + " Restaurante",
            "address": fake.address(),
            "contact": create_fake_contact_info().model_dump(),
            "cuisine_type": sample(cuisine_types, k=randint(1, 3)),
            "hours": create_fake_schedule().model_dump(),
            "location": create_fake_geolocation().model_dump() if uniform(0, 1) > 0.2 else None,
            "rating": round(uniform(3.0, 5.0), 1),
            "created_at": fake.past_datetime(start_date="-2y"),
            "updated_at": fake.past_datetime(start_date="-1y")
        }
        restaurants.append(restaurant_data)
    return restaurants

def create_fake_nutritional_info():
    return NutritionalInfo(
        calories=uniform(200, 1500),
        protein=uniform(5, 100),
        carbs=uniform(10, 200),
        fat=uniform(5, 100)
    )

def create_fake_menu_item(restaurant_ids, num_items_per_restaurant=15):
    menu_items_data = []
    categories = ['Entrantes', 'Platos Principales', 'Postres', 'Bebidas', 'Guarniciones', 'Sopas', 'Ensaladas']
    tags = ['Vegano', 'Vegetariano', 'Sin Gluten', 'Picante', 'Popular', 'Nuevo', 'Especialidad']
    ingredients = ['Tomate', 'Lechuga', 'Queso', 'Pollo', 'Carne', 'Pescado', 'Arroz', 'Pasta', 'Cebolla', 'Pimiento', 'Champiñones']
    
    for rest_id in restaurant_ids:
        for _ in range(num_items_per_restaurant):
            item_data = {
                "restaurant_id": rest_id, 
                "name": fake.word().capitalize() + " " + choice(['Delicioso', 'Especial', 'Casero', 'Grill']),
                "description": fake.sentence(nb_words=10),
                "price": round(uniform(5.0, 50.0), 2),
                "category": choice(categories),
                "tags": sample(tags, k=randint(0, 3)),
                "available": uniform(0, 1) > 0.1,
                "image_url": fake.image_url() if uniform(0, 1) > 0.3 else None,
                "nutritional_info": create_fake_nutritional_info().model_dump() if uniform(0, 1) > 0.4 else None,
                "ingredients": sample(ingredients, k=randint(3, 7)),
                "created_at": fake.past_datetime(start_date="-1y"),
                "updated_at": fake.past_datetime(start_date="-6m")
            }
            menu_items_data.append(item_data)
    return menu_items_data

def create_fake_order_item(menu_items_for_restaurant):
    item_ref = choice(menu_items_for_restaurant)
    return OrderItem(
        item_id=str(item_ref['_id']), 
        name=item_ref['name'],
        price=item_ref['price'],
        quantity=randint(1, 5),
        special_instructions=fake.sentence(nb_words=5) if uniform(0, 1) > 0.7 else None
    )

def create_fake_customer_info():
    return CustomerInfo(
        name=fake.name(),
        email=fake.email(),
        phone=fake.phone_number() if uniform(0, 1) > 0.3 else None,
        address=fake.address() if uniform(0, 1) > 0.5 else None
    )

def create_fake_order(restaurant_ids, all_menu_items, num_orders_per_restaurant=20):
    orders_data = []
    statuses = ['pendiente', 'en_proceso', 'listo_para_recoger', 'en_camino', 'entregado', 'cancelado']
    payment_methods = ['efectivo', 'tarjeta_credito', 'tarjeta_debito', 'paypal', 'transferencia']
    payment_statuses = ['pendiente', 'pagado', 'fallido', 'reembolsado']

    for rest_id in restaurant_ids:
        menu_items_for_restaurant = [item for item in all_menu_items if item['restaurant_id'] == rest_id]
        if not menu_items_for_restaurant:
            continue

        for i in range(num_orders_per_restaurant):
            order_items = [create_fake_order_item(menu_items_for_restaurant).model_dump() for _ in range(randint(1, 5))]
            total_amount = sum(item['price'] * item['quantity'] for item in order_items)
            status = choice(statuses)
            payment_status = choice(payment_statuses)
            delivery_time = fake.future_datetime(end_date="+2h") if status == 'entregado' else None

            order_data = {
                "restaurant": "Restaurante ID:" + str(rest_id), 
                "date": fake.past_datetime(start_date="-6m"),
                "customer": create_fake_customer_info().model_dump(),
                "items": order_items,
                "total_amount": round(total_amount, 2),
                "status": status,
                "payment_method": choice(payment_methods) if payment_status == 'pagado' else None,
                "payment_status": payment_status,
                "delivery_time": delivery_time,
                "rating": randint(1, 5) if status == 'entregado' else None,
                "feedback": fake.sentence(nb_words=15) if status == 'entregado' and uniform(0, 1) > 0.5 else None,
                "created_at": fake.past_datetime(start_date="-1y"),
                "updated_at": fake.past_datetime(start_date="-1m")
            }
            orders_data.append(order_data)
    return orders_data

def create_fake_review(restaurant_ids, order_ids, num_reviews_per_restaurant=5):
    reviews_data = []
    
    for rest_id in restaurant_ids:
        orders_for_restaurant = [order for order in order_ids if order.get('restaurant', '').endswith(str(rest_id)) and order.get('status') == 'entregado']
        orders_to_review = sample(orders_for_restaurant, k=min(num_reviews_per_restaurant, len(orders_for_restaurant)))

        for order_ref in orders_to_review:
            has_response = uniform(0, 1) > 0.6
            response_info = ResponseInfo(
                text=fake.sentence(nb_words=10),
                date=fake.future_datetime(end_date="+1w")
            ).model_dump() if has_response else None

            review_data = {
                "restaurant_id": rest_id,
                "order_id": order_ref['_id'],
                "customer": CustomerBasicInfo(name=order_ref['customer']['name'], email=order_ref['customer']['email']).model_dump(),
                "rating": randint(1, 5),
                "comment": fake.paragraph(nb_sentences=randint(1, 4)),
                "date": fake.future_datetime(end_date="+2d"),
                "helpful_votes": randint(0, 50),
                "response": response_info,
                "created_at": fake.past_datetime(start_date="-6m"),
                "updated_at": fake.past_datetime(start_date="-1w")
            }
            reviews_data.append(review_data)
    return reviews_data

async def insert_fake_data(num_restaurants=10, num_items_per_restaurant=15, num_orders_per_restaurant=20, num_reviews_per_restaurant=5):
    print("⏳ Generando datos falsos...")
    
    restaurants_to_insert = create_fake_restaurant(num_restaurants)
    print(f"   - Generados {len(restaurants_to_insert)} restaurantes.")
    
    try:
        await db.restaurants.drop()
        result_rest = await db.restaurants.insert_many(restaurants_to_insert)
        inserted_restaurant_ids = result_rest.inserted_ids
        print(f"✅ Insertados {len(inserted_restaurant_ids)} restaurantes.")
    except Exception as e:
        print(f"❌ Error insertando restaurantes: {e}")
        return

    menu_items_to_insert = create_fake_menu_item(inserted_restaurant_ids, num_items_per_restaurant)
    print(f"   - Generados {len(menu_items_to_insert)} items de menú.")
    
    try:
        await db.menu_items.drop()
        result_items = await db.menu_items.insert_many(menu_items_to_insert)
        print(f"✅ Insertados {len(result_items.inserted_ids)} items de menú.")
        all_inserted_menu_items = await db.menu_items.find({"_id": {"$in": result_items.inserted_ids}}).to_list(None)
    except Exception as e:
        print(f"❌ Error insertando items de menú: {e}")
        return

    orders_to_insert = create_fake_order(inserted_restaurant_ids, all_inserted_menu_items, num_orders_per_restaurant)
    print(f"   - Generados {len(orders_to_insert)} pedidos.")
    
    try:
        await db.orders.drop()
        result_orders = await db.orders.insert_many(orders_to_insert)
        print(f"✅ Insertados {len(result_orders.inserted_ids)} pedidos.")
        all_inserted_orders = await db.orders.find({"_id": {"$in": result_orders.inserted_ids}}).to_list(None)
    except Exception as e:
        print(f"❌ Error insertando pedidos: {e}")
        return

    reviews_to_insert = create_fake_review(inserted_restaurant_ids, all_inserted_orders, num_reviews_per_restaurant)
    print(f"   - Generadas {len(reviews_to_insert)} reseñas.")

    try:
        await db.reviews.drop()
        result_reviews = await db.reviews.insert_many(reviews_to_insert)
        print(f"✅ Insertadas {len(result_reviews.inserted_ids)} reseñas.")
    except Exception as e:
        print(f"❌ Error insertando reseñas: {e}")
        return

    print("\n✨ Proceso completado.")

if __name__ == "__main__":
    asyncio.run(insert_fake_data(
        num_restaurants=250,
        num_items_per_restaurant=25,
        num_orders_per_restaurant=200,
        num_reviews_per_restaurant=20
    )) 