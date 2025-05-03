from fastapi import FastAPI
from app.routers import orders

# Create FastAPI application
app = FastAPI(
    title="API de Pedidos y Reseñas",
    description="API para gestionar pedidos y reseñas de restaurantes",
    version="1.0.0"
)

# Include routers
app.include_router(orders.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Pedidos y Reseñas"} 