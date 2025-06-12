from dataclasses import dataclass
from datetime import datetime

@dataclass
class Empresa:
    cnpj: str
    razao_social: str
    nome_fantasia: str
    pasta: str
    nomes_anteriores: list[str] = None

@dataclass
class GuiaMetadados:
    competencia: str
    vencimento: str
    valor: float
    numero_documento: str
    caminho_arquivo: str
    data_processamento: datetime = datetime.now()

