"""Aplicação FastAPI - Gestão de Clientes e Usuários"""
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from config.db import criar_tabelas
from routes.auth import auth_router
from routes.requisicao import requisicao_router
from routes.imovel import imovel_router


# Criar tabelas ao iniciar
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     criar_tabelas()
#     yield
#     # Shutdown (opcional)


# Inicializar app com suporte a rate limit
# limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="PtAPI",
    description="Sistema de Gestão de Clientes e Usuários",
    version="1.0.0",
    # lifespan=lifespan
)

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, lambda request, exc: {"detail": "Rate limit exceeded"})

# Incluir rotas
app.include_router(auth_router)
app.include_router(requisicao_router)
app.include_router(imovel_router)


@app.get("/")
def root():
    """Health check"""
    return {"message": "PtAPI v1.0.0 - Tudo funcionando! ✅"}
