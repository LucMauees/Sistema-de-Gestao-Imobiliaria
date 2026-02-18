"""Rotas de Requisições - requerem autenticação JWT"""
from fastapi import APIRouter, Depends

from config.auth import obter_usuario_atual
from models.contratado import Contratado

requisicao_router = APIRouter(prefix="/requisicao", tags=["requisicao"])


@requisicao_router.get("/listar")
async def listar_requisicoes(_usuario: Contratado = Depends(obter_usuario_atual)):
    """Lista todas as requisições (autenticado)."""
    return {"message": "Lista de requisições"}


@requisicao_router.post("/criar")
async def criar_requisicao(_usuario: Contratado = Depends(obter_usuario_atual)):
    """Cria uma nova requisição (autenticado)."""
    return {"message": "Requisição criada"}


@requisicao_router.delete("/deletar/{requisicao_id}")
async def deletar_requisicao(
    requisicao_id: int,
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    """Deleta uma requisição (autenticado)."""
    return {"message": f"Requisição {requisicao_id} deletada"}


@requisicao_router.put("/atualizar/{requisicao_id}")
async def atualizar_requisicao(
    requisicao_id: int,
    _usuario: Contratado = Depends(obter_usuario_atual),
):
    """Atualiza uma requisição (autenticado)."""
    return {"message": f"Requisição {requisicao_id} atualizada"}
