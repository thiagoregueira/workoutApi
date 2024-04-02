from fastapi import APIRouter, status, Body, HTTPException
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.atleta.models import AtletaModel
from workout_api.categoria.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from datetime import datetime
from uuid import uuid4
from pydantic import UUID4
from sqlalchemy.future import select


router = APIRouter()


@router.post("/", summary="Criar um novo atleta", status_code=status.HTTP_201_CREATED, response_model=AtletaOut)
async def create_atleta(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...) ) -> AtletaOut:

    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=atleta_in.categoria.nome))).scalars().first()
    

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"A categoria {atleta_in.categoria.nome} não existe")

    centro = (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome))).scalars().first()

    if not centro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"O centro de treinamento {atleta_in.centro_treinamento.nome} não existe")

    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={"categoria", "centro_treinamento"}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao inserir dados no banco: " + str(e))

    return atleta_out


@router.get("/", summary="Listar todos os atletas", response_model=list[AtletaOut], status_code=status.HTTP_200_OK)
async def listar_atletas(db_session: DatabaseDependency) -> list[AtletaOut]:
    atletas: list[AtletaOut] = (await db_session.execute(select(AtletaModel))).scalars().all()

    if not atletas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum atleta criado!")

    return [AtletaOut.model_validate(atleta) for atleta in atletas]


@router.get("/{atleta_id}", summary="Exibir um atleta", response_model=AtletaOut, status_code=status.HTTP_200_OK)
async def listar_atleta(atleta_id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=atleta_id))).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta com id {atleta_id} não encontrado")
    return atleta


@router.patch("/{atleta_id}", summary="Editar um atleta pelo ID", response_model=AtletaOut, status_code=status.HTTP_200_OK)
async def editar_atleta(atleta_id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=atleta_id))).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta com id {atleta_id} não encontrado")

    atleta_update = atleta_up.model_dump()

    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta


@router.delete("/{atleta_id}", summary="Deletar um atleta pelo ID", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_atleta(atleta_id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=atleta_id))).scalars().first()
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Atleta com id {atleta_id} não encontrado")
    await db_session.delete(atleta)
    await db_session.commit()
    return None



