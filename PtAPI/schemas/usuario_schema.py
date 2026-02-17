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
        """Valida formato e dígitos verificadores do CPF"""
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, v))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            raise ValueError('CPF deve conter exatamente 11 dígitos')
        
        # Verifica se todos os dígitos são iguais (CPF inválido)
        if cpf == cpf[0] * 11:
            raise ValueError('CPF inválido: todos os dígitos são iguais')
        
        # Valida primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10:
            digito1 = 0
        if digito1 != int(cpf[9]):
            raise ValueError('CPF inválido: primeiro dígito verificador incorreto')
        
        # Valida segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10:
            digito2 = 0
        if digito2 != int(cpf[10]):
            raise ValueError('CPF inválido: segundo dígito verificador incorreto')
        
        return cpf
    
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
    cpf: str  # CPF completo (considerar mascarar em produção)
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr
    senha: str = Field(..., min_length=1, description="Senha do usuário")


class TokenResponse(BaseModel):
    """Resposta com token de autenticação"""
    access_token: str
    token_type: str = "bearer"
