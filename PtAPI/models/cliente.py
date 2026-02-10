"""Modelos de Cliente (PF e PJ com herança)"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType
from config.db import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)  # Discriminador: 'fisica' ou 'juridica'
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    status = Column(ChoiceType([('ativo', 'Ativo'), ('inativo', 'Inativo')]), default='ativo', nullable=False)
    senha = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    endereco = Column(String, nullable=False)
    
    __mapper_args__ = {
        "polymorphic_identity": "cliente",
        "polymorphic_on": tipo
    }

    # 1 Cliente -> N Contratos
    contratos = relationship(
        "Contratos",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )

    # 1 Cliente -> N Imoveis
    imoveis = relationship(
        "Imovel",
        back_populates="cliente",
        cascade="all, delete-orphan"
    )


class ClienteFisica(Cliente):
    __tablename__ = "clientes_fisica"
    
    id = Column(Integer, ForeignKey("clientes.id"), primary_key=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    rg = Column(String, unique=True, index=True, nullable=False)
    data_de_nascimento = Column(Date, nullable=False)
    
    # 1 ClienteFisica -> N SocioRepresentante
    participacoes = relationship(
        "SocioRepresentante",
        back_populates="pessoa_fisica",
        cascade="all, delete-orphan"
    )
    
    __mapper_args__ = {
        "polymorphic_identity": "fisica"
    }


class ClienteJuridica(Cliente):
    __tablename__ = "clientes_juridica"
    
    id = Column(Integer, ForeignKey("clientes.id"), primary_key=True)
    cnpj = Column(String, unique=True, index=True, nullable=False)
    razao_social = Column(String, nullable=False)
    nome_fantasia = Column(String, nullable=False)
    inscricao_estadual = Column(String, nullable=True)
    endereco_comercial = Column(String, nullable=False)
    data_fundacao = Column(Date, nullable=True)

    # N ClienteJuridica -> N SocioRepresentante
    socios_representantes = relationship(
        "SocioRepresentante",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    
    __mapper_args__ = {
        "polymorphic_identity": "juridica"
    }
