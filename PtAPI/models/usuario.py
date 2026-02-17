"""Modelo de Usuário (pessoa física simplificada)"""
from sqlalchemy import Column, Integer, String, Date
from config.db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    rg = Column(String, unique=True, index=True, nullable=False)
    data_de_nascimento = Column(Date, nullable=False)
