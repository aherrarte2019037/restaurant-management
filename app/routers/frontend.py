from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from bson import ObjectId
from bson.errors import InvalidId
from app.database import db # Importar db

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
        # Obtener datos básicos del restaurante para mostrar en la página
        restaurant_data = await db.restaurants.find_one({"_id": object_id})
        
        if not restaurant_data:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        # Convertir ObjectId a str para la plantilla (aunque el modelo ya debería hacerlo)
        if '_id' in restaurant_data:
             restaurant_data['id'] = str(restaurant_data['_id'])
             del restaurant_data['_id'] # Usar solo 'id' en la plantilla

        # Pasar los datos básicos del restaurante a la plantilla
        return templates.TemplateResponse(
            "restaurant_detail.html", 
            {"request": request, "restaurant": restaurant_data}
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
        restaurant_data = await db.restaurants.find_one(
            {"_id": object_id},
            {"_id": 1, "name": 1} # Solo necesitamos ID y nombre (proyección)
        )
        
        if not restaurant_data:
            raise HTTPException(status_code=404, detail="Restaurante no encontrado")
            
        restaurant_data['id'] = str(restaurant_data['_id'])
        del restaurant_data['_id']

        return templates.TemplateResponse(
            "restaurant_orders.html", 
            {"request": request, "restaurant": restaurant_data} # Pasar datos a la plantilla
        )
    except InvalidId:
        raise HTTPException(status_code=404, detail="ID de restaurante inválido")
    except Exception as e:
        print(f"Error cargando página de pedidos: {e}")
        raise HTTPException(status_code=500, detail="Error interno al cargar la página") 