"""Inicialização do pacote routes"""
from routes.auth import auth_router
from routes.requisicao import requisicao_router
from routes.imovel import imovel_router

__all__ = ["auth_router", "requisicao_router", "imovel_router"]
