from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
from datetime import datetime

from models import Tarea, TareaCreate, TareaUpdate
from database import coleccion_tareas, verificar_conexion

# Instancia principal de FastAPI
app = FastAPI(
    title="API TODO App Profesional - SENA ADSO",
    description="API RESTful asíncrona con FastAPI y MongoDB (FARM Stack).",
    version="1.0.0"
)

# Configuración de CORS para permitir conexión con clientes Frontend (React, Angular, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Evento de inicio del servidor
@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()


# ENDPOINTS RESTFUL ASÍNCRONOS


@app.get("/", tags=["Raíz"])
async def root():
    return {
        "mensaje": "Bienvenido a la API TODO App Asíncrona con MongoDB (SENA ADSO)",
        "documentacion": "/docs"
    }

@app.post(
    "/tareas",
    response_model=Tarea,
    status_code=status.HTTP_201_CREATED,
    tags=["Tareas"],
    summary="Crear una nueva tarea en MongoDB"
)
async def create_tarea(tarea_in: TareaCreate):
    """
    Guarda una tarea de forma asíncrona en la colección 'tareas' de MongoDB:
    - Asigna la fecha de creación actual.
    - Evita títulos duplicados (lanza HTTP 400 Bad Request).
    """
    # 1. Validar que no exista otra tarea con el mismo título
    tarea_existente = await coleccion_tareas.find_one({"titulo": tarea_in.titulo})
    if tarea_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una tarea registrada con el título '{tarea_in.titulo}'."
        )

    # 2. Preparar el diccionario del documento
    nueva_tarea = tarea_in.model_dump()
    nueva_tarea["fecha_creacion"] = datetime.now()

    # 3. Insertar asíncronamente en MongoDB
    resultado = await coleccion_tareas.insert_one(nueva_tarea)

    # 4. Recuperar el documento recién creado por su _id ObjectId
    tarea_creada = await coleccion_tareas.find_one({"_id": resultado.inserted_id})
    return tarea_creada

@app.get(
    "/tareas",
    response_model=List[Tarea],
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Listar todas las tareas"
)
async def get_tareas():
    """Recupera asíncronamente todos los documentos de la colección de MongoDB."""
    tareas = []
    # Usar cursor asíncrono de Motor
    cursor = coleccion_tareas.find()
    async for documento in cursor:
        tareas.append(documento)
    return tareas

@app.get(
    "/tareas/{id}",
    response_model=Tarea,
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Buscar tarea por ObjectId"
)
async def get_tarea_por_id(id: str):
    """Busca una tarea específica por su ObjectId de MongoDB."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido de MongoDB."
        )

    tarea = await coleccion_tareas.find_one({"_id": ObjectId(id)})
    if tarea:
        return tarea

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La tarea con ID '{id}' no fue encontrada en la base de datos."
    )

@app.put(
    "/tareas/{id}",
    response_model=Tarea,
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Actualizar estado o campos de una tarea"
)
async def update_tarea(id: str, tarea_update: TareaUpdate):
    """Actualiza los campos de un documento en MongoDB por su _id."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    # Extraer solo los datos enviados en la petición
    datos_a_actualizar = tarea_update.model_dump(exclude_unset=True)

    if len(datos_a_actualizar) >= 1:
        resultado_actualizacion = await coleccion_tareas.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos_a_actualizar}
        )

        if resultado_actualizacion.modified_count == 1 or resultado_actualizacion.matched_count == 1:
            tarea_modificada = await coleccion_tareas.find_one({"_id": ObjectId(id)})
            return tarea_modificada

    # Si no se modificó o no se encontró el ID
    tarea_existente = await coleccion_tareas.find_one({"_id": ObjectId(id)})
    if tarea_existente:
        return tarea_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar, la tarea con ID '{id}' no existe."
    )

@app.delete(
    "/tareas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Tareas"],
    summary="Eliminar tarea de MongoDB"
)
async def delete_tarea(id: str):
    """Elimina permanentemente un documento de MongoDB por su ObjectId."""
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId válido."
        )

    resultado_eliminacion = await coleccion_tareas.delete_one({"_id": ObjectId(id)})

    if resultado_eliminacion.deleted_count == 1:
        return {"mensaje": f"Tarea con ID '{id}' eliminada exitosamente de MongoDB."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar. La tarea con ID '{id}' no existe en la base de datos."
    )
