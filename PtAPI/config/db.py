"""Configuração do banco de dados"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada. Adicione a variável no arquivo .env")

# Base declarativa PRIMEIRO (antes de importar modelos)
Base = declarative_base()

# Engine
db = create_engine(DATABASE_URL)

# SessionLocal para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db)


def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    # Importar modelos AQUI para registrar no metadata
    from models.cliente import Cliente, ClienteFisica, ClienteJuridica
    from models.contratado import Contratado
    from models.contrato import Contratos
    from models.imovel import Imovel, ImovelUnidade, RegistroMatricula, ContaServico
    from models.socio import SocioRepresentante
    
    Base.metadata.create_all(bind=db)
    print(f"✅ Tabelas criadas: {list(Base.metadata.tables.keys())}")


def get_db():
    """Dependency para injetar sessão do banco em rotas"""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()

