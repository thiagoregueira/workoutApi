from fastapi import APIRouter, Body, status, HTTPException
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency
from uuid import uuid4
from sqlalchemy.future import select
from pydantic import UUID4



router = APIRouter()


@router.post("/", summary="Cria um novo centro de treinamento", status_code=status.HTTP_201_CREATED ,response_model=CentroTreinamentoOut)
async def create_centro(db_session: DatabaseDependency, centro_in: CentroTreinamentoIn = Body(...)) -> CentroTreinamentoOut:
    centro_out = CentroTreinamentoOut(id=uuid4(), **centro_in.model_dump())
    centro_model = CentroTreinamentoModel(**centro_out.model_dump())

    existing_centro = await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=centro_in.nome))
    if existing_centro.scalar() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Centro já existe")

    db_session.add(centro_model)
    await db_session.commit()

    return centro_out


@router.get("/", summary="Listar todos os centros", status_code=status.HTTP_200_OK ,response_model=list[CentroTreinamentoOut])
async def get_all_categories(db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centros: list[CentroTreinamentoOut] = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()

    if not centros:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum centro cadastrado")

    return centros


@router.get("/{id}", summary="Consultar um centro pelo ID", status_code=status.HTTP_200_OK ,response_model=CentroTreinamentoOut)
async def get_one_category(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Centro não encontrado com o id {id}")

    return centro