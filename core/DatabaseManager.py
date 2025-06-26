import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Importando o modelo de guia
from .models import GuiaMetadados

class DatabaseManager:
    """
    Gerencia todas as operações de banco de dados para o sistema de organização de guias.
    Cada empresa tem seu próprio banco de dados SQLite.
    
    Atributos:
        db_path (Path): Caminho para o arquivo de banco de dados da empresa
        conn (sqlite3.Connection): Conexão com o banco de dados
    """
    
    def __init__(self, db_path: Path):
        """
        Inicializa o gerenciador de banco de dados para uma empresa específica.
        
        Args:
            db_path: Caminho para o arquivo .db da empresa
        """
        self.db_path = db_path
        self.conn = None
        self.logger = logging.getLogger(f"{__name__}.DatabaseManager")
        
        # Garante que o diretório pai existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()

    def _initialize_database(self):
        """Cria o banco de dados e as tabelas se não existirem."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Criação da tabela de guias
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS guias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competencia TEXT NOT NULL,
                vencimento TEXT NOT NULL,
                valor REAL NOT NULL,
                numero_documento TEXT NOT NULL,
                caminho_arquivo TEXT UNIQUE NOT NULL,
                data_processamento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)
            # data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            # Índices para consultas rápidas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_competencia ON guias (competencia);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vencimento ON guias (vencimento);")
            
            self.conn.commit()
            self.logger.info(f"Banco de dados inicializado: {self.db_path}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise RuntimeError(f"Falha na inicialização do banco de dados: {str(e)}")

    def insert_guia(self, guia: GuiaMetadados) -> bool:
        """
        Insere uma nova guia no banco de dados.
        
        Args:
            guia: Objeto GuiaMetadados com os dados da guia
            
        Returns:
            True se bem-sucedido, False em caso de erro
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            INSERT INTO guias (competencia, vencimento, valor, numero_documento, caminho_arquivo, data_processamento)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                guia.competencia,
                guia.vencimento,
                guia.valor,
                guia.numero_documento,
                str(guia.caminho_arquivo),  # Convertendo Path para string
                guia.data_processamento
            ))
            self.conn.commit()
            self.logger.info(f"Guia inserida: {guia.numero_documento} - {guia.competencia}")
            return True
            
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Guia já existe no banco de dados: {str(e)}")
            return False
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inserir guia: {str(e)}")
            return False

    def find_duplicate_guia(self, guia: GuiaMetadados) -> Optional[GuiaMetadados]:
        """
        Encontra uma guia duplicada baseada em competência, vencimento e valor.
        
        Args:
            guia: Guia a ser verificada
            
        Returns:
            GuiaMetadados existente se encontrada duplicata, None caso contrário
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT competencia, vencimento, valor, numero_documento, caminho_arquivo, data_processamento
            FROM guias
            WHERE competencia = ? AND vencimento = ? AND valor = ?
            ORDER BY data_processamento DESC
            LIMIT 1
            """, (guia.competencia, guia.vencimento, guia.valor))
            
            result = cursor.fetchone()
            if result:
                return GuiaMetadados(*result)
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao buscar duplicata: {str(e)}")
            return None

    def get_all_guias(self) -> List[GuiaMetadados]:
        """Retorna todas as guias no banco de dados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT competencia, vencimento, valor, numero_documento, caminho_arquivo, data_processamento
            FROM guias
            ORDER BY data_processamento DESC
            """)
            print(cursor.fetchall())
            return [GuiaMetadados(*row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter todas as guias: {str(e)}")
            return []

    def update_guia_path(self, old_path: Path, new_path: Path) -> bool:
        """
        Atualiza o caminho de um arquivo de guia no banco de dados.
        
        Útil quando arquivos são movidos ou renomeados.
        
        Args:
            old_path: Caminho antigo do arquivo
            new_path: Novo caminho do arquivo
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE guias
            SET caminho_arquivo = ?
            WHERE caminho_arquivo = ?
            """, (str(new_path), str(old_path)))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao atualizar caminho da guia: {str(e)}")
            return False

    def delete_guia(self, caminho_arquivo: Path) -> bool:
        """
        Remove uma guia do banco de dados.
        
        Args:
            caminho_arquivo: Caminho do arquivo da guia a ser removida
            
        Returns:
            True se removida com sucesso, False caso contrário
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM guias WHERE caminho_arquivo = ?", (str(caminho_arquivo),))
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao deletar guia: {str(e)}")
            return False

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.logger.info("Conexão com banco de dados fechada")

    def __enter__(self):
        """Suporte para gerenciamento de contexto (with statement)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que a conexão é fechada ao sair do contexto"""
        self.close()