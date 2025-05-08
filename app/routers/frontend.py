from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from bson import ObjectId
from bson.errors import InvalidId
from app.database import db # Importar db
from datetime import datetime # Importar datetime
from typing import Any, Dict, List

# --- Función Auxiliar para Serialización --- 
def make_json_serializable(data: Any) -> Any:
    """Convierte recursivamente ObjectId y datetime a string."""
    if isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    if isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    # Añadir más conversiones si es necesario (ej. Decimal)
    return data
# -------------------------------------------

# Configurar directorio de plantillas relativo a este archivo o al main?
# Asumiendo que main.py ya configuró templates correctamente
# Importar templates desde main (o reconfigurar aquí)
# De forma simple, reconfiguramos:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(
    # Podríamos poner un prefijo como /web si no queremos que sea la raíz
    tags=["Frontend"],
    include_in_schema=False # No incluir estas rutas en la documentación OpenAPI
)

@router.get("/", response_class=HTMLResponse)
async def read_frontend_root(request: Request): # Cambiado de read_orders_page
    """Sirve la página principal del frontend (lista de restaurantes)."""
    # El JS en index.html se encargará de cargar la lista
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/restaurants/{restaurant_id}/dashboard", response_class=HTMLResponse)
async def restaurant_dashboard(request: Request, restaurant_id: str):
    """Sirve la página de detalles (Menú/Reseñas) para un restaurante específico."""
    try:
        object_id = ObjectId(restaurant_id)
        restaurant_doc = await db.restaurants.find_one({"_id": object_id})
        
        if not restaurant_doc:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        # Usar la función auxiliar para asegurar que todo sea serializable
        serializable_data = make_json_serializable(restaurant_doc)
        
        # Renombrar _id a id para la plantilla
        if '_id' in serializable_data:
            serializable_data['id'] = serializable_data.pop('_id')

        return templates.TemplateResponse(
            "restaurant_detail.html", 
            {"request": request, "restaurant": serializable_data} 
        )
    except InvalidId:
        # Podríamos mostrar una página de error bonita aquí también
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")
    except Exception as e:
        # Manejo de otros errores de base de datos o inesperados
        print(f"Error cargando dashboard de restaurante: {e}")
        raise HTTPException(status_code=500, detail="Error interno al cargar la página") 

# Restaurar la ruta para la página de pedidos
@router.get("/restaurants/{restaurant_id}/orders", response_class=HTMLResponse)
async def restaurant_orders_page(request: Request, restaurant_id: str):
    """Sirve la página dedicada a los pedidos de un restaurante."""
    try:
        object_id = ObjectId(restaurant_id)
        restaurant_doc = await db.restaurants.find_one(
            {"_id": object_id},
            {"_id": 1, "name": 1} # (proyección)
        )
        
        if not restaurant_doc:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        # Usar la función auxiliar aquí también (aunque solo trae _id y name)
        serializable_data = make_json_serializable(restaurant_doc)
        if '_id' in serializable_data:
            serializable_data['id'] = serializable_data.pop('_id')

        return templates.TemplateResponse(
            "restaurant_orders.html", 
            {"request": request, "restaurant": serializable_data} # Pasar datos a la plantilla
        )
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")
    except Exception as e:
        print(f"Error cargando página de pedidos: {e}")
        raise HTTPException(status_code=500, detail="Error interno al cargar la página") 