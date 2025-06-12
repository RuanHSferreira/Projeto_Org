import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from core import PDFProcessor, DatabaseManager, FileManager
from core.models import Empresa
import config
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / 'organizer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PDFHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.pdf_processor = PDFProcessor()
        self.file_manager = FileManager(config)
        self.empresas = self.carregar_empresas()
    
    def carregar_empresas(self) -> dict:
        with open(self.config.EMPRESAS_JSON, 'r') as f:
            dados = json.load(f)
            return {cnpj: Empresa(cnpj=cnpj, **info) for cnpj, info in dados.items()}
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.processar_pdf(Path(event.src_path))
    
    def processar_pdf(self, caminho_pdf: Path):
        try:
            # Etapa 1: Extrair metadados do PDF
            metadados = self.pdf_processor.extrair_metadados(str(caminho_pdf))
            
            # Etapa 2: Identificar empresa
            empresa = self.identificar_empresa(metadados.cnpj)
            if not empresa:
                self.file_manager.mover_para_conflitos(caminho_pdf, "EMPRESA_NAO_REGISTRADA")
                return
            
            # Etapa 3: Gerenciar banco de dados da empresa
            db_path = self.config.PASTA_DB_EMPRESAS / f"{empresa.cnpj}.db"
            db_manager = DatabaseManager(db_path)
            
            # Etapa 4: Verificar duplicatas/recalculadas
            self.verificar_e_processar(caminho_pdf, metadados, empresa, db_manager)
            
        except Exception as e:
            logger.error(f"Erro processando {caminho_pdf}: {str(e)}")
            self.file_manager.mover_para_conflitos(caminho_pdf, "ERRO_PROCESSAMENTO")
    
    def identificar_empresa(self, cnpj: str) -> Empresa:
        # Lógica para encontrar empresa mesmo com mudança de razão social
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        return self.empresas.get(cnpj_limpo)
    
    def verificar_e_processar(self, caminho_pdf: Path, metadados: GuiaMetadados, 
                            empresa: Empresa, db_manager: DatabaseManager):
        # Implementar lógica de comparação com guias existentes
        pass  # (Sua implementação anterior aqui)


if __name__ == "__main__":
    event_handler = PDFHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path=str(config.PASTA_ENTRADA), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(config.TEMPO_VERIFICACAO)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
