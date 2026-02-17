"""Rotas de Requisições"""
from fastapi import APIRouter

requisicao_router = APIRouter(prefix="/requisicao", tags=["requisicao"])


@requisicao_router.get("/listar")
async def listar_requisicoes():
    """Lista todas as requisições"""
    return {"message": "Lista de requisições"}


@requisicao_router.post("/criar")
async def criar_requisicao():
    """Cria uma nova requisição"""
    return {"message": "Requisição criada"}


@requisicao_router.delete("/deletar/{requisicao_id}")
async def deletar_requisicao(requisicao_id: int):
    """Deleta uma requisição"""
    return {"message": f"Requisição {requisicao_id} deletada"}


@requisicao_router.put("/atualizar/{requisicao_id}")
async def atualizar_requisicao(requisicao_id: int):
    """Atualiza uma requisição"""
    return {"message": f"Requisição {requisicao_id} atualizada"}
