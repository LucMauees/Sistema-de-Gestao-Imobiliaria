"""Schemas Pydantic para Usuario"""
from pydantic import BaseModel, EmailStr, validator, Field
from datetime import date
import re


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150, description="Nome do usuário")
    senha: str = Field(..., min_length=8, max_length=255, description="Senha com mínimo 8 caracteres")
    email: EmailStr
    cpf: str = Field(..., pattern=r'^\d{11}$', description="CPF com 11 dígitos")
    rg: str = Field(..., min_length=5, max_length=20, description="RG")
    data_de_nascimento: date
    
    @validator('email')
    def normalize_email(cls, v):
        """Normaliza email: minúsculas e sem espaços"""
        return v.lower().strip()
    
    @validator('cpf')
    def validate_cpf_format(cls, v):
        """Valida formato do CPF"""
        if not v.isdigit() or len(v) != 11:
            raise ValueError('CPF deve conter exatamente 11 dígitos')
        return v
    
    @validator('nome')
    def validate_nome(cls, v):
        """Valida nome: apenas letras e espaços"""
        if not re.match(r'^[a-zA-ZáéíóúàâêôãõçÁÉÍÓÚÀÂÊÔÃÕÇ\s]+$', v):
            raise ValueError('Nome deve conter apenas letras')
        return v.strip()
    
    @validator('senha')
    def validate_senha(cls, v):
        """Valida força da senha"""
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve conter pelo menos 1 letra maiúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter pelo menos 1 número')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Senha deve conter pelo menos 1 caractere especial')
        return v


class UsuarioResponse(BaseModel):
    """Resposta com apenas dados públicos"""
    id: int
    nome: str
    email: str
    cpf: str
    
    class Config:
        from_attributes = True
