from pydantic import BaseModel, UUID4
from pydantic import Field
from typing import Annotated
from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        extra = "forbid"
        from_attributes = True


class OutMixin(BaseSchema):
    id: Annotated[UUID4, Field(description="Identificador", example="123e4567-e89b-12d3-a456-426614174000")]
    created_at: Annotated[datetime, Field(description="Data de criação")]