from pathlib import Path
from typing import Final
from os import listdir

# Crie uma classe para agrupar as configurações
class AppConfig:
    # Diretórios base
    BASE_DIR: Final[Path] = Path(__file__).parent.resolve()
    
    # Pastas
    PASTA_ENTRADA: Final[Path] = BASE_DIR / "pasta_entrada"
    PASTA_PROCESSADOS: Final[Path] = BASE_DIR / "pasta_processados"
    PASTA_CONFLITOS: Final[Path] = BASE_DIR / "pasta_conflitos"
    PASTA_DB_EMPRESAS: Final[Path] = BASE_DIR / "data" / "Metadados"
    LOGS_DIR: Final[Path] = BASE_DIR / "logs"
    
    
    # Conteudo da pasta se tiver
    PASTA_CONTEUDO: Final[list] = listdir(PASTA_ENTRADA)

    # Arquivos
    EMPRESAS_JSON: Final[Path] = BASE_DIR / "data" / "empresas.json"
    
    # Configurações de execução
    TEMPO_VERIFICACAO: Final[int] = 300  # segundos

    def __init__(self):
        # Criar diretórios se não existirem
        for pasta in [
            self.PASTA_ENTRADA, self.PASTA_PROCESSADOS, self.PASTA_CONFLITOS,
            self.PASTA_DB_EMPRESAS, self.LOGS_DIR
        ]:
            pasta.mkdir(parents=True, exist_ok=True)

# Instância única de configuração
config = AppConfig()