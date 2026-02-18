"""Modelo de Contratado (usuários do sistema)."""
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from config.db import Base


class Contratado(Base):
    """
    Contratados são os usuários do sistema (login/cadastro).
    """
    __tablename__ = "contratados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    rg = Column(String, unique=True, index=True, nullable=False)
    data_de_nascimento = Column(Date, nullable=False)
    servico = Column(String, nullable=False)

    # 1 Contratado -> N Contratos
    contratos = relationship(
        "Contratos",
        back_populates="contratado",
        cascade="all, delete-orphan"
    )
