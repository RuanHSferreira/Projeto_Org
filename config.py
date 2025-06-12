from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.resolve()

# Pastas
PASTA_ENTRADA = BASE_DIR / "pasta_entrada"
PASTA_PROCESSADOS = BASE_DIR / "pasta_processados"
PASTA_CONFLITOS = BASE_DIR / "pasta_conflitos"
PASTA_DB_EMPRESAS = BASE_DIR / "data" / "Metadados"
LOGS_DIR = BASE_DIR / "logs"

# Arquivos
EMPRESAS_JSON = BASE_DIR / "data" / "empresas.json"

# Configurações de execução
TEMPO_VERIFICACAO = 300  # segundos

# Criar diretórios se não existirem
for pasta in [PASTA_ENTRADA, PASTA_PROCESSADOS, PASTA_CONFLITOS, 
              PASTA_DB_EMPRESAS, LOGS_DIR]:
    pasta.mkdir(parents=True, exist_ok=True)
