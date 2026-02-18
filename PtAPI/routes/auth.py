"""Rotas de Autenticação e Usuários"""
from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from typing import List
import logging
import re
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

from config.db import SessionLocal, get_db
from config.auth import criar_token, obter_usuario_atual
from models.contratado import Contratado
from schemas.contratado_schema import ContratadoCreate, ContratadoResponse, ContratadoLogin, TokenResponse

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


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha plana corresponde ao hash"""
    return pwd_context.verify(senha_plana, senha_hash)


def log_cadastro(email: str, status_code: int, detalhes: str = ""):
    """Log de cadastro sem expor dados sensíveis"""
    logger.info(f"Cadastro - Email: {email[:3]}***@***.*** | Status: {status_code} | {detalhes}")


@auth_router.post("/CadastroUsuarios", status_code=201, response_model=ContratadoResponse)
# @limiter.limit("5/minute")
def criar_usuario(request: Request, payload: ContratadoCreate, db=Depends(get_db)):
    """
    Cria novo contratado (usuário do sistema) com:
    - Hash de senha (argon2)
    - Validação completa de payload
    - Email normalizado
    """
    try:
        email_normalizado = payload.email.lower().strip()
        
        # Verificar se email já existe
        existente = db.query(Contratado).filter(Contratado.email == email_normalizado).first()
        if existente:
            log_cadastro(email_normalizado, 400, "Email duplicado")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
        
        # Verificar se CPF já existe
        cpf_existente = db.query(Contratado).filter(Contratado.cpf == payload.cpf).first()
        if cpf_existente:
            log_cadastro(email_normalizado, 400, "CPF duplicado")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado")
        
        senha_hash = hash_senha(payload.senha)
        
        contratado = Contratado(
            nome=payload.nome,
            senha=senha_hash,
            email=email_normalizado,
            cpf=payload.cpf,
            rg=payload.rg,
            data_de_nascimento=payload.data_de_nascimento,
            servico=payload.servico
        )
        
        db.add(contratado)
        db.commit()
        db.refresh(contratado)
        
        log_cadastro(email_normalizado, 201, "Contratado criado com sucesso")
        
        return ContratadoResponse(
            id=contratado.id,
            nome=contratado.nome,
            email=contratado.email,
            cpf=contratado.cpf,
            servico=contratado.servico
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


@auth_router.post("/login", response_model=TokenResponse, status_code=200)
def login(payload: ContratadoLogin, db=Depends(get_db)):
    """
    Autentica um contratado (usuário do sistema) e retorna um token JWT.
    """
    try:
        email_normalizado = payload.email.lower().strip()
        contratado = db.query(Contratado).filter(Contratado.email == email_normalizado).first()
        
        if not contratado:
            logger.warning(f"Tentativa de login com email inexistente: {email_normalizado[:3]}***")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        if not verificar_senha(payload.senha, contratado.senha):
            logger.warning(f"Tentativa de login com senha incorreta: {email_normalizado[:3]}***")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        access_token = criar_token(contratado.id)
        logger.info(f"Login bem-sucedido: {email_normalizado[:3]}***")
        
        return TokenResponse(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao fazer login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar login"
        )


@auth_router.get("/usuarios", response_model=List[ContratadoResponse])
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db=Depends(get_db),
    usuario_atual: Contratado = Depends(obter_usuario_atual)
):
    """
    Lista contratados (usuários do sistema). Requer autenticação via token JWT.
    """
    try:
        contratados = db.query(Contratado).offset(skip).limit(limit).all()
        return [
            ContratadoResponse(
                id=c.id,
                nome=c.nome,
                email=c.email,
                cpf=c.cpf,
                servico=c.servico
            )
            for c in contratados
        ]
    except Exception as e:
        logger.exception(f"Erro ao listar usuários: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar usuários")

