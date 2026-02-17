

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from config.db import Base


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

    # Endereço detalhado
    rua = Column(String, nullable=False)
    numero = Column(String, nullable=True)
    complemento = Column(String, nullable=True)
    bairro = Column(String, nullable=False)
    municipio = Column(String, nullable=False)
    estado = Column(String(2), nullable=False)
    cep = Column(String, nullable=False)

    # Metragem
    area_total_m2 = Column(Float, nullable=False, default=0.0)

    # Status de ocupação do imóvel principal
    status_ocupacao = Column(ChoiceType([('ocupado', 'Ocupado'), ('desocupado', 'Desocupado')]), default='desocupado', nullable=False)

    # Vinculo com cliente proprietário
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="imoveis")
    unidades = relationship("ImovelUnidade", back_populates="imovel", cascade="all, delete-orphan")
    registros = relationship("RegistroMatricula", back_populates="imovel", cascade="all, delete-orphan")
    contas = relationship("ContaServico", back_populates="imovel", cascade="all, delete-orphan")

    def calcular_iptu_proporcional(self, valor_total_iptu: float, desconto_cota_unica: float = 0.0):
        """Calcula a distribuição proporcional do IPTU por unidade com base na área.

        Retorna uma lista de dicionários com (unidade_id, nome, area_m2, iptu_proporcional, iptu_com_desconto)
        """
        unidades = [u for u in self.unidades if u.area_m2 and u.area_m2 > 0]
        total_area_locada = sum(u.area_m2 for u in unidades)
        if total_area_locada == 0:
            return []

        resultado = []
        for u in unidades:
            proporcao = u.area_m2 / total_area_locada
            iptu = round(valor_total_iptu * proporcao, 2)
            iptu_descontado = round((valor_total_iptu - desconto_cota_unica) * proporcao, 2) if desconto_cota_unica else iptu
            resultado.append({
                'unidade_id': u.id,
                'nome_unidade': u.nome_unidade,
                'area_m2': u.area_m2,
                'iptu': iptu,
                'iptu_com_desconto': iptu_descontado
            })
        return resultado

    # def gerar_pdf_iptu_por_unidade(self, unidade, valor_total_iptu: float, desconto_cota_unica: float = 0.0) -> bytes:
    #     """Gera um PDF simples com o cálculo do IPTU para a unidade fornecida e retorna bytes.

    #     Dependência: reportlab (pip install reportlab)
    #     """
    #     buffer = io.BytesIO()
    #     c = canvas.Canvas(buffer, pagesize=A4)
    #     width, height = A4

    #     margem = 20 * mm
    #     y = height - margem

    #     c.setFont('Helvetica-Bold', 14)
    #     c.drawString(margem, y, f'Comprovante de Cálculo de IPTU - {unidade.nome_unidade}')
    #     y -= 12 * mm

    #     c.setFont('Helvetica', 11)
    #     c.drawString(margem, y, f'Imóvel: {self.rua}, {self.numero} - {self.bairro} / {self.municipio}-{self.estado}')
    #     y -= 8 * mm
    #     c.drawString(margem, y, f'Unidade: {unidade.nome_unidade} | Área: {unidade.area_m2} m²')
    #     y -= 8 * mm
    #     c.drawString(margem, y, f'Valor total IPTU: R$ {valor_total_iptu:.2f}')
    #     y -= 8 * mm
    #     if desconto_cota_unica:
    #         c.drawString(margem, y, f'Desconto cota única aplicado: R$ {desconto_cota_unica:.2f}')
    #         y -= 8 * mm

    #     # cálculo proporcional
    #     distribuicao = self.calcular_iptu_proporcional(valor_total_iptu, desconto_cota_unica)
    #     encontrado = next((d for d in distribuicao if d['unidade_id'] == unidade.id), None)
    #     if encontrado:
    #         c.drawString(margem, y, f'IPTU proporcional (sem desconto): R$ {encontrado["iptu"]:.2f}')
    #         y -= 8 * mm
    #         c.drawString(margem, y, f'IPTU proporcional (com desconto): R$ {encontrado["iptu_com_desconto"]:.2f}')
    #         y -= 12 * mm

    #     c.setFont('Helvetica-Oblique', 9)
    #     c.drawString(margem, y, f'Gerado em: {datetime.utcnow().isoformat()} UTC')

    #     c.showPage()
    #     c.save()
    #     buffer.seek(0)
    #     return buffer.read()


class ImovelUnidade(Base):
    __tablename__ = "imovel_unidades"

    id = Column(Integer, primary_key=True)
    imovel_id = Column(Integer, ForeignKey("imoveis.id"), nullable=False)
    nome_unidade = Column(String, nullable=False)
    area_m2 = Column(Float, nullable=False, default=0.0)
    descricao = Column(Text, nullable=True)

    # Vincular a um contrato individual (opcional)
    contrato_id = Column(Integer, ForeignKey("contratos.id"), nullable=True)

    # Status de ocupação por unidade
    status = Column(ChoiceType([('ocupado', 'Ocupado'), ('desocupado', 'Desocupado')]), default='desocupado', nullable=False)

    imovel = relationship("Imovel", back_populates="unidades")
    contrato = relationship("Contratos")


class RegistroMatricula(Base):
    __tablename__ = "registro_matriculas"

    id = Column(Integer, primary_key=True)
    imovel_id = Column(Integer, ForeignKey("imoveis.id"), nullable=False)
    matricula = Column(String, nullable=False)
    cartorio = Column(String, nullable=False)
    cnm = Column(String, nullable=True)
    inscricao_municipal = Column(String, nullable=True)
    data_registro = Column(DateTime, default=datetime.utcnow)
    atual = Column(Boolean, default=False)

    imovel = relationship("Imovel", back_populates="registros")


class ContaServico(Base):
    __tablename__ = "contas_servicos"

    id = Column(Integer, primary_key=True)
    imovel_id = Column(Integer, ForeignKey("imoveis.id"), nullable=False)
    tipo = Column(ChoiceType([('energia', 'Energia'), ('agua', 'Água'), ('telefonia', 'Telefonia'), ('outro', 'Outro')]), nullable=False)
    numero_conta = Column(String, nullable=False)
    fornecedor = Column(String, nullable=True)
    status = Column(ChoiceType([('ativo', 'Ativo'), ('suspenso', 'Suspenso'), ('encerrado', 'Encerrado')]), default='ativo', nullable=False)
    observacoes = Column(Text, nullable=True)

    imovel = relationship("Imovel", back_populates="contas")
