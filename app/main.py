from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routers import orders, restaurants, menu_items, reviews, frontend
from app.db.indexes import create_indexes
from fastapi.openapi.utils import get_openapi
import os

# Configurar directorio de plantillas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@asynccontextmanager
async def lifespan(app: FastAPI):
  await create_indexes()
  yield

# Create FastAPI application
app = FastAPI(
    title="API de Pedidos y Reseñas",
    description="API para gestionar pedidos y reseñas de restaurantes",
    version="1.0.0",
    lifespan=lifespan
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
        
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Include routers
app.include_router(frontend.router)
app.include_router(orders.router)
app.include_router(restaurants.router)
app.include_router(menu_items.router)
app.include_router(reviews.router)
 