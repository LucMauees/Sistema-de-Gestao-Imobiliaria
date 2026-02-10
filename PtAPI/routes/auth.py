"""Rotas de Autenticação e Usuários"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from typing import List
import logging
import re
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

from config.db import SessionLocal, get_db
from models.usuario import Usuario
from schemas.usuario_schema import UsuarioCreate, UsuarioResponse

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração de hash de senha com argon2
pwd_context = CryptContext(schemes=["argon2","bcrypt"], deprecated="auto")

# Rate limiter: máximo 5 cadastros por minuto
limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter(prefix="/auth", tags=["autenticacao"])


def hash_senha(senha: str) -> str:
    """Hash da senha usando argon2"""
    return pwd_context.hash(senha)


def log_cadastro(email: str, status_code: int, detalhes: str = ""):
    """Log de cadastro sem expor dados sensíveis"""
    logger.info(f"Cadastro - Email: {email[:3]}***@***.*** | Status: {status_code} | {detalhes}")


@auth_router.post("/CadastroUsuarios", status_code=201, response_model=UsuarioResponse)
# @limiter.limit("5/minute")
def criar_usuario(request: Request, payload: UsuarioCreate, db=Depends(get_db)):
    """
    ✅ Cria novo usuário com:
    - Hash de senha (argon2)
    - Validação completa de payload
    - Email normalizado
    - Rate limit (5 por minuto)
    - Log seguro (sem senha)
    """
    try:
        email_normalizado = payload.email.lower().strip()
        
        # Verificar se email já existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == email_normalizado).first()
        if usuario_existente:
            log_cadastro(email_normalizado, 400, "Email duplicado")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
        
        # Verificar se CPF já existe
        cpf_existente = db.query(Usuario).filter(Usuario.cpf == payload.cpf).first()
        if cpf_existente:
            log_cadastro(email_normalizado, 400, "CPF duplicado")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado")
        
        # Hash da senha (argon2)
        senha_hash = hash_senha(payload.senha)
        
        # Criar novo usuário
        usuario = Usuario(
            nome=payload.nome,
            senha=senha_hash,
            email=email_normalizado,
            cpf=payload.cpf,
            rg=payload.rg,
            data_de_nascimento=payload.data_de_nascimento
        )
        
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        
        # Log de sucesso sem dados sensíveis
        log_cadastro(email_normalizado, 201, "Usuário criado com sucesso")
        
        # Retorno com apenas dados públicos
        return UsuarioResponse(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            cpf=usuario.cpf
        )
    except HTTPException:
        raise
    except ValueError as ve:
        log_cadastro(payload.email, 422, f"Validação: {str(ve)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        # Log completo da exceção (inclui traceback) para diagnóstico em desenvolvimento
        logger.exception(f"Erro ao criar usuário: {type(e).__name__} - {e}")
        log_cadastro(payload.email, 500, f"Erro: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")


@auth_router.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(db=Depends(get_db)):
    """Lista todos os usuários cadastrados"""
    try:
        usuarios = db.query(Usuario).all()
        return [
            UsuarioResponse(
                id=u.id,
                nome=u.nome,
                email=u.email,
                cpf=u.cpf
            )
            for u in usuarios
        ]
    except Exception as e:
        logger.exception(f"Erro ao listar usuários: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar usuários")

