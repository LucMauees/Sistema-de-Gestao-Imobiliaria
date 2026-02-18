"""Aplicação FastAPI - Gestão de Clientes e Usuários"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from config.db import criar_tabelas
from routes.auth import auth_router
from routes.requisicao import requisicao_router
from routes.imovel import imovel_router

load_dotenv()


# Criar tabelas ao iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    criar_tabelas()
    yield
    # Shutdown (opcional)


# Inicializar app com suporte a rate limit
# limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="PtAPI",
    description="Sistema de Gestão de Clientes e Usuários",
    version="1.0.0",
    # lifespan=lifespan
)

# Configurar CORS
# Obter origens permitidas da variável de ambiente ou usar padrão seguro
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Se não houver origens configuradas, usar lista vazia (mais seguro)
# Em desenvolvimento, você pode usar: ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
if not allowed_origins:
    # Em produção, defina ALLOWED_ORIGINS no .env
    # Para desenvolvimento local, descomente a linha abaixo:
    # allowed_origins = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    allowed_origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, lambda request, exc: {"detail": "Rate limit exceeded"})

# Incluir rotas
# Segurança: rotas públicas = login e cadastro; demais rotas exigem Bearer JWT (obter_usuario_atual)
app.include_router(auth_router)
app.include_router(requisicao_router)
app.include_router(imovel_router)


@app.get("/")
def root():
    """Health check"""
    return {"message": "PtAPI v1.0.0 - Tudo funcionando! ✅"}
