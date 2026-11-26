from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

class _ObjectIdPydanticAnnotation:
    """Adaptador para validar y serializar ObjectId de MongoDB en Pydantic v2"""
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("ID inválido de MongoDB (ObjectId)")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )

# Tipo de dato reutilizable para Pydantic
PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]

class TareaBase(BaseModel):
    titulo: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Título descriptivo de la tarea",
        example="Diseñar la arquitectura del proyecto FARM Stack"
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=500,
        description="Detalles adicionales o requerimientos",
        example="Definir los modelos en Pydantic y las rutas en FastAPI"
    )
    completada: bool = Field(
        default=False,
        description="Estado de cumplimiento de la tarea"
    )

class TareaCreate(TareaBase):
    """Modelo utilizado para recibir solicitudes POST de creación"""
    pass

class TareaUpdate(BaseModel):
    """Modelo para solicitudes PUT (Campos opcionales para edición)"""
    titulo: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    completada: Optional[bool] = None

class Tarea(TareaBase):
    """Modelo completo de respuesta que incluye el ID de MongoDB y la fecha"""
    id: PyObjectId = Field(alias="_id", description="Identificador único ObjectId de MongoDB")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de registro")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "654321789abcdef012345678",
                "titulo": "Implementar endpoints asíncronos",
                "descripcion": "Uso de async/await con el driver Motor",
                "completada": False,
                "fecha_creacion": "2026-11-05T18:30:00"
            }
        }
    )
