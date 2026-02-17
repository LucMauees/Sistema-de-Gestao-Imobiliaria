"""Configuração de Autenticação JWT"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config.db import get_db
from models.usuario import Usuario

# Carregar variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "XtO1B5qaj5D6b3ogS1gZThYqrS2WSAqYcQ2WfUrRhxc")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


def criar_token(usuario_id: int) -> str:
    """Cria um token JWT para o usuário"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {"sub": str(usuario_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verificar_token(token: str) -> Optional[int]:
    """Verifica e decodifica um token JWT, retorna o ID do usuário"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            return None
        return int(usuario_id)
    except JWTError:
        return None


def obter_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency para obter o usuário atual autenticado.
    Usar em rotas que requerem autenticação.
    
    Exemplo:
        @router.get("/protegida")
        def rota_protegida(usuario_atual: Usuario = Depends(obter_usuario_atual)):
            return {"usuario_id": usuario_atual.id}
    """
    token = credentials.credentials
    usuario_id = verificar_token(token)
    
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario
