"""Modelo de Sócio/Representante"""
from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType
from config.db import Base


class SocioRepresentante(Base):
    __tablename__ = "socios_representantes"
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("clientes_juridica.id"), nullable=False)
    pessoa_fisica_id = Column(Integer, ForeignKey("clientes_fisica.id"), nullable=False)
    cargo = Column(
        ChoiceType([
            ('socio', 'Sócio'),
            ('socio_administrador', 'Sócio Administrador'),
            ('administrador', 'Administrador'),
            ('diretor', 'Diretor'),
            ('presidente', 'Presidente')
        ]),
        nullable=False
    )
    data_admissao = Column(Date, nullable=True)
    
    # N SocioRepresentante -> 1 ClienteJuridica
    empresa = relationship(
        "ClienteJuridica",
        back_populates="socios_representantes"
    )
    
    # N SocioRepresentante -> 1 ClienteFisica
    pessoa_fisica = relationship(
        "ClienteFisica",
        back_populates="participacoes"
    )
