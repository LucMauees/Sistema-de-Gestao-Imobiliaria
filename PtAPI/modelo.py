from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os 
from dotenv import load_dotenv
from sqlalchemy_utils.types import ChoiceType

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
db = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)

Base = declarative_base()

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



class Contratado(Base):
    __tablename__ = "contratados"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    servico = Column(String, nullable=False)

    # 1 Contratado -> N Contratos
    contratos = relationship(
        "Contratos",
        back_populates="contratado",
        cascade="all, delete-orphan"
    )

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

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True)
    endereco = Column(String, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # N Imoveis -> 1 Cliente
    cliente = relationship("Cliente", back_populates="imoveis")


# Criar todas as tabelas
def criar_tabelas():
    Base.metadata.create_all(bind=db)
    
if __name__ == "__main__":
    criar_tabelas()
