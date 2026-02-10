"""Inicialização do pacote models com import de todos os modelos"""
from models.usuario import Usuario
from models.cliente import Cliente, ClienteFisica, ClienteJuridica
from models.socio import SocioRepresentante
from models.contratos import Contratos, Imovel, Contratado

__all__ = [
    "Usuario",
    "Cliente",
    "ClienteFisica",
    "ClienteJuridica",
    "SocioRepresentante",
    "Contratos",
    "Imovel",
    "Contratado",
]
