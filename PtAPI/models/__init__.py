"""Inicialização do pacote models com import de todos os modelos.

Ordem dos imports: cliente, contratado, contrato, imovel, socio
(garante que relacionamentos por nome de classe resolvam corretamente).
"""
from models.cliente import Cliente, ClienteFisica, ClienteJuridica
from models.contratado import Contratado
from models.contrato import Contratos
from models.imovel import Imovel, ImovelUnidade, RegistroMatricula, ContaServico
from models.socio import SocioRepresentante

__all__ = [
    "Cliente",
    "ClienteFisica",
    "ClienteJuridica",
    "Contratado",
    "Contratos",
    "Imovel",
    "ImovelUnidade",
    "RegistroMatricula",
    "ContaServico",
    "SocioRepresentante",
]
