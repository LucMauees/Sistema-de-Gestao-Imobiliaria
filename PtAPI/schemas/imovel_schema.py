"""Schemas Pydantic para Imóvel, Unidades, Registros e Contas"""
from pydantic import BaseModel, Field, constr
from typing import Optional, List


class EnderecoBase(BaseModel):
    rua: str
    numero: Optional[str]
    complemento: Optional[str]
    bairro: str
    municipio: str
    estado: constr(min_length=2, max_length=2)
    cep: str


class ImovelCreate(EnderecoBase):
    area_total_m2: float = Field(..., gt=0)
    cliente_id: int


class ImovelResponse(EnderecoBase):
    id: int
    area_total_m2: float

    class Config:
        from_attributes = True


class ImovelUnidadeCreate(BaseModel):
    nome_unidade: str
    area_m2: float = Field(..., gt=0)
    descricao: Optional[str]
    contrato_id: Optional[int]


class ImovelUnidadeResponse(ImovelUnidadeCreate):
    id: int

    class Config:
        from_attributes = True


class RegistroMatriculaCreate(BaseModel):
    matricula: str
    cartorio: str
    cnm: Optional[str]
    inscricao_municipal: Optional[str]
    atual: Optional[bool] = False


class RegistroMatriculaResponse(RegistroMatriculaCreate):
    id: int
    data_registro: Optional[str]

    class Config:
        from_attributes = True


class ContaServicoCreate(BaseModel):
    tipo: str
    numero_conta: str
    fornecedor: Optional[str]
    status: Optional[str] = 'ativo'
    observacoes: Optional[str]


class ContaServicoResponse(ContaServicoCreate):
    id: int

    class Config:
        from_attributes = True


class IPTUCalculationRequest(BaseModel):
    valor_total_iptu: float = Field(..., gt=0)
    desconto_cota_unica: Optional[float] = 0.0


class IPTUUnitResult(BaseModel):
    unidade_id: int
    nome_unidade: str
    area_m2: float
    iptu: float
    iptu_com_desconto: float


class IPTUCalculationResponse(BaseModel):
    distribuicao: List[IPTUUnitResult]
