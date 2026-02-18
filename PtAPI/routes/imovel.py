"""Rotas para gerenciamento de Imóveis, Unidades, Registros e Contas"""
from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi.responses import StreamingResponse
from typing import List
import io

from config.db import get_db
from config.auth import obter_usuario_atual
from models.contratado import Contratado
from sqlalchemy.orm import Session

from models.imovel import Imovel, ImovelUnidade, RegistroMatricula, ContaServico
from schemas.imovel_schema import (
    ImovelCreate, ImovelResponse, ImovelUnidadeCreate, ImovelUnidadeResponse,
    RegistroMatriculaCreate, RegistroMatriculaResponse, ContaServicoCreate, ContaServicoResponse,
    IPTUCalculationRequest, IPTUCalculationResponse, IPTUUnitResult
)

imovel_router = APIRouter(prefix="/imoveis", tags=["imoveis"])


@imovel_router.post("/", response_model=ImovelResponse, status_code=201)
def criar_imovel(
    payload: ImovelCreate,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = Imovel(
        rua=payload.rua,
        numero=payload.numero,
        complemento=payload.complemento,
        bairro=payload.bairro,
        municipio=payload.municipio,
        estado=payload.estado,
        cep=payload.cep,
        area_total_m2=payload.area_total_m2,
        cliente_id=payload.cliente_id
    )
    db.add(imovel)
    db.commit()
    db.refresh(imovel)
    return imovel


@imovel_router.get("/{imovel_id}", response_model=ImovelResponse)
def obter_imovel(
    imovel_id: int,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel


@imovel_router.post("/{imovel_id}/unidades", response_model=ImovelUnidadeResponse, status_code=201)
def criar_unidade(
    imovel_id: int,
    payload: ImovelUnidadeCreate,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    unidade = ImovelUnidade(
        imovel_id=imovel_id,
        nome_unidade=payload.nome_unidade,
        area_m2=payload.area_m2,
        descricao=payload.descricao,
        contrato_id=payload.contrato_id
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)
    return unidade


@imovel_router.post("/{imovel_id}/registros", response_model=RegistroMatriculaResponse, status_code=201)
def criar_registro(
    imovel_id: int,
    payload: RegistroMatriculaCreate,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    registro = RegistroMatricula(
        imovel_id=imovel_id,
        matricula=payload.matricula,
        cartorio=payload.cartorio,
        cnm=payload.cnm,
        inscricao_municipal=payload.inscricao_municipal,
        atual=payload.atual
    )
    # marcar outros como não atual se este for atual
    if payload.atual:
        db.query(RegistroMatricula).filter(RegistroMatricula.imovel_id == imovel_id).update({"atual": False})
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@imovel_router.post("/{imovel_id}/contas", response_model=ContaServicoResponse, status_code=201)
def criar_conta(
    imovel_id: int,
    payload: ContaServicoCreate,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    conta = ContaServico(
        imovel_id=imovel_id,
        tipo=payload.tipo,
        numero_conta=payload.numero_conta,
        fornecedor=payload.fornecedor,
        status=payload.status,
        observacoes=payload.observacoes
    )
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return conta


@imovel_router.post("/{imovel_id}/iptu/calc", response_model=IPTUCalculationResponse)
def calcular_iptu(
    imovel_id: int,
    payload: IPTUCalculationRequest,
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    distribuicao = imovel.calcular_iptu_proporcional(payload.valor_total_iptu, payload.desconto_cota_unica or 0.0)
    resultados = [IPTUUnitResult(**d) for d in distribuicao]
    return {"distribuicao": resultados}


@imovel_router.get("/{imovel_id}/unidades/{unidade_id}/iptu/pdf")
def gerar_pdf_iptu(
    imovel_id: int,
    unidade_id: int,
    valor_total_iptu: float = Query(...),
    desconto_cota_unica: float = Query(0.0),
    db: Session = Depends(get_db),
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    unidade = db.query(ImovelUnidade).filter(ImovelUnidade.id == unidade_id, ImovelUnidade.imovel_id == imovel_id).first()
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    pdf_bytes = imovel.gerar_pdf_iptu_por_unidade(unidade, valor_total_iptu, desconto_cota_unica)
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")
