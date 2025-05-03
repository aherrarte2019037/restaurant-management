from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi

# MongoDB connection URI
uri = "mongodb+srv://root:l6laZfVO5NU1AQux@proyectodb.alvl9qk.mongodb.net/?retryWrites=true&w=majority&appName=ProyectoDB"

# Create a new client and connect to the server with SSL configuration
client = MongoClient(
    uri,
    server_api=ServerApi('1'),
    ssl=True,
    tlsAllowInvalidCertificates=True,
    tlsCAFile=certifi.where()
)

# Test connection and get database
try:
    client.admin.command('ping')
    print("✅ Conectado a MongoDB Atlas")
    db = client['Jefe']
except Exception as e:
    print("❌ No se pudo conectar:", e)
    db = None 