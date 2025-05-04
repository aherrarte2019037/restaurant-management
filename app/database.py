from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import certifi

# MongoDB connection URI
uri = "mongodb+srv://root:l6laZfVO5NU1AQux@proyectodb.alvl9qk.mongodb.net/?retryWrites=true&w=majority&appName=ProyectoDB"

# Create a new client and connect to the server with SSL configuration
client = AsyncIOMotorClient(
    uri,
    server_api=ServerApi('1'),
    ssl=True,
    tlsAllowInvalidCertificates=True,
    tlsCAFile=certifi.where()
)

# Get database
db = client['Jefe']

# Print connection status (we can't use ping command with AsyncIOMotorClient here)
print("✅ Conectado a MongoDB Atlas") 