from workout_api.contrib.schemas import BaseSchema
from typing import Annotated
from pydantic import Field, UUID4


class CategoriaIn(BaseSchema):
    nome: Annotated[str, Field(description="Nome da categoria", example="Scale", max_length=10)]


class CategoriaOut(CategoriaIn):
    id: Annotated[UUID4, Field(description="Identificador da categoria", example="123e4567-e89b-12d3-a456-426614174000")]