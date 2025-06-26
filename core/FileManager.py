import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import AppConfig
    

class FileManager:
    
    def __init__(self, config: 'AppConfig'):
        self._config = config

    def mover_para_conflitos(self, caminho_pdf: Path, motivo: str):
        shutil.move(caminho_pdf, self._config.PASTA_CONFLITOS)
        
