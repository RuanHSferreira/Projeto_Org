import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from core import PDFProcessor, DatabaseManager, FileManager
from core.models import Empresa, GuiaMetadados
from config import config
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
    def __init__(self, config) -> None:
        self.config = config
        self.pdf_processor = PDFProcessor
        self.file_manager = FileManager.FileManager(config)
        self.empresas = self.carregar_empresas()
        self.check_initial()
        return None
    
    # Função para verificar a pasta quando inicio o programa
    def check_initial(self):
        if self.config.PASTA_CONTEUDO:
            for i in self.config.PASTA_CONTEUDO:
                self.processar_pdf(Path(self.config.PASTA_ENTRADA / i))

    def carregar_empresas(self) -> dict:
        with open(self.config.EMPRESAS_JSON, 'r') as f:
            dados = json.load(f)
            return {cnpj: Empresa(cnpj=cnpj, **info) for cnpj, info in dados.items()}
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            time.sleep(0.2)
            self.processar_pdf(Path(event.src_path))
    
    def processar_pdf(self, caminho_pdf: Path):
        try:
            # Etapa 1: Extrair metadados do PDF
            metadados = self.pdf_processor.PDFProcessor(str(caminho_pdf)).dados

            # Etapa 2: Identificar empresa
            # empresa = self.identificar_empresa(metadados['CNPJ'])
            #print(empresa.cnpj)
            if not self.empresas.get(metadados.cnpj):
                self.file_manager.mover_para_conflitos(caminho_pdf, "EMPRESA_NAO_REGISTRADA")
                return
            
            # Limpas caracteres indesejaveis
            self._cnpj_limp = self.empresas.get(metadados.cnpj).cnpj.replace(".", "_").replace("/", "_")

            # # Etapa 3: Gerenciar banco de dados da empresa
            self._db_path = self.config.PASTA_DB_EMPRESAS / f"{self._cnpj_limp}.db"
            self._db_manager = DatabaseManager.DatabaseManager(self._db_path)
            print(self._db_manager.get_all_guias())
            #print(metadados)
            # # Etapa 4: Verificar duplicatas/recalculadas
            # self.verificar_e_processar(caminho_pdf, metadados, empresa, db_manager)
            
        except Exception as e:
            logger.error(f"Erro processando {caminho_pdf}: {str(e)}")
            #self.file_manager.mover_para_conflitos(caminho_pdf, "ERRO_PROCESSAMENTO")
    
    def verificar_e_processar(self, caminho_pdf: Path, metadados: GuiaMetadados, 
                            empresa: Empresa, db_manager: DatabaseManager):
        # Implementar lógica de comparação com guias existentes
        pass  # (Sua implementação anterior aqui)


if __name__ == "__main__":
   
    
    #PDFHandler(config)
    
    
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
