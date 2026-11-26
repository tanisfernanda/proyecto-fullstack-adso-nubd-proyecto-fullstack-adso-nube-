from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

# Cargar la URI y nombre de base de datos desde el archivo .env
MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="adso_db")

# Cliente asíncrono de MongoDB
client = AsyncIOMotorClient(MONGODB_URL)

# Referencia a la base de datos relacional/documental
database = client[DATABASE_NAME]

# Colección de tareas en MongoDB
coleccion_tareas = database["tareas"]

async def verificar_conexion():
    """Función de comprobación de estado de la conexión al iniciar la API"""
    try:
        await client.admin.command('ping')
        print(f"Conexión exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error de conexión a MongoDB: {e}")
