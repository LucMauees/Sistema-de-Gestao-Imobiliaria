"""Modelo de Contrato (vínculo Cliente–Contratado)."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from config.db import Base


class Contratos(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    contratado_id = Column(Integer, ForeignKey("contratados.id"), nullable=False)
    detalhes = Column(String, nullable=False)

    # N Contratos -> 1 Cliente
    cliente = relationship("Cliente", back_populates="contratos")

    # N Contratos -> 1 Contratado
    contratado = relationship("Contratado", back_populates="contratos")
