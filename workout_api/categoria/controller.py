from fastapi import APIRouter, Body, status, HTTPException
from workout_api.categoria.schemas import CategoriaIn, CategoriaOut 
from workout_api.categoria.models import CategoriaModel
from workout_api.contrib.dependencies import DatabaseDependency
from uuid import uuid4
from sqlalchemy.future import select
from pydantic import UUID4


router = APIRouter()


@router.post("/", summary="Cria uma nova categoria", status_code=status.HTTP_201_CREATED ,response_model=CategoriaOut)
async def create_categoria(db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    existing_category = await db_session.execute(select(CategoriaModel).filter_by(nome=categoria_in.nome))
    if existing_category.scalar() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe")

    db_session.add(categoria_model)
    await db_session.commit()

    return categoria_out


@router.get("/", summary="Listar todas as categorias", status_code=status.HTTP_200_OK ,response_model=list[CategoriaOut])
async def get_all_categories(db_session: DatabaseDependency) -> list[CategoriaOut]:
    categorias: list[CategoriaOut] = (await db_session.execute(select(CategoriaModel))).scalars().all()

    if not categorias:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma categoria cadastrada")

    return categorias


@router.get("/{id}", summary="Consultar categoria pelo id", status_code=status.HTTP_200_OK ,response_model=CategoriaOut)
async def get_one_category(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Categoria não encontrada com o id {id}")

    return categoria