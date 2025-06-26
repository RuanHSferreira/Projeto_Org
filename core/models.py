from dataclasses import dataclass
from datetime import datetime

@dataclass
class Empresa:
    cnpj: str
    razao_social: str
    pasta: str
    caminho_atual: str
    nomes_anteriores: list[str] = None
    

@dataclass
class GuiaMetadados:
    cnpj: str
    competencia: str
    vencimento: str
    vencimento_original: str
    valor: float
    numero_documento: str
    caminho_arquivo: str
    data_processamento: datetime = datetime.now().isoformat(sep=' ', timespec='seconds')

