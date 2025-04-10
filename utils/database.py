import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from utils.constants import (
    ERRO_CONEXAO_DB,
    ERRO_EXECUCAO_DB,
    ERRO_FECHAMENTO_DB
)

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        
    def get_connection(self) -> sqlite3.Connection:
        """
        Estabelece conexão com o banco de dados.
        
        Returns:
            Conexão com o banco de dados
            
        Raises:
            Exception: Se não conseguir estabelecer conexão
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"{ERRO_CONEXAO_DB}: {str(e)}")
            raise Exception(ERRO_CONEXAO_DB)
            
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executa uma query e retorna os resultados.
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros da query
            
        Returns:
            Lista de resultados
            
        Raises:
            Exception: Se houver erro na execução
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"{ERRO_EXECUCAO_DB}: {str(e)}")
            raise Exception(ERRO_EXECUCAO_DB)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"{ERRO_FECHAMENTO_DB}: {str(e)}")
                    
    def execute_many(self, query: str, params: List[tuple]) -> None:
        """
        Executa uma query com múltiplos parâmetros.
        
        Args:
            query: Query SQL a ser executada
            params: Lista de parâmetros
            
        Raises:
            Exception: Se houver erro na execução
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
        except Exception as e:
            logger.error(f"{ERRO_EXECUCAO_DB}: {str(e)}")
            raise Exception(ERRO_EXECUCAO_DB)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"{ERRO_FECHAMENTO_DB}: {str(e)}")
                    
    def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> None:
        """
        Executa múltiplas queries em uma transação.
        
        Args:
            queries: Lista de tuplas (query, params)
            
        Raises:
            Exception: Se houver erro na execução
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for query, params in queries:
                cursor.execute(query, params)
                
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"{ERRO_EXECUCAO_DB}: {str(e)}")
            raise Exception(ERRO_EXECUCAO_DB)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"{ERRO_FECHAMENTO_DB}: {str(e)}")
                    
    def get_condutor(self, cnh: str) -> Optional[Dict[str, Any]]:
        """
        Busca um condutor pelo número da CNH.
        
        Args:
            cnh: Número da CNH
            
        Returns:
            Dados do condutor ou None se não encontrado
        """
        query = "SELECT * FROM condutores WHERE cnh = ?"
        results = self.execute_query(query, (cnh,))
        return results[0] if results else None
        
    def get_veiculo(self, placa: str) -> Optional[Dict[str, Any]]:
        """
        Busca um veículo pela placa.
        
        Args:
            placa: Placa do veículo
            
        Returns:
            Dados do veículo ou None se não encontrado
        """
        query = "SELECT * FROM veiculos WHERE placa = ?"
        results = self.execute_query(query, (placa,))
        return results[0] if results else None
        
    def get_veiculos_em_uso(self) -> List[Dict[str, Any]]:
        """
        Busca todos os veículos em uso.
        
        Returns:
            Lista de veículos em uso
        """
        query = """
            SELECT v.*, c.nome as condutor_nome, c.cnh as condutor_cnh
            FROM veiculos v
            LEFT JOIN registros r ON v.id = r.veiculo_id
            LEFT JOIN condutores c ON r.condutor_id = c.id
            WHERE r.data_entrada IS NULL
        """
        return self.execute_query(query)
        
    def get_condutores_disponiveis(self) -> List[Dict[str, Any]]:
        """
        Busca todos os condutores disponíveis.
        
        Returns:
            Lista de condutores disponíveis
        """
        query = """
            SELECT c.*
            FROM condutores c
            LEFT JOIN registros r ON c.id = r.condutor_id
            WHERE r.data_entrada IS NULL
            OR r.id IS NULL
        """
        return self.execute_query(query)
        
    def get_veiculos_disponiveis(self) -> List[Dict[str, Any]]:
        """
        Busca todos os veículos disponíveis.
        
        Returns:
            Lista de veículos disponíveis
        """
        query = """
            SELECT v.*
            FROM veiculos v
            LEFT JOIN registros r ON v.id = r.veiculo_id
            WHERE r.data_entrada IS NULL
            OR r.id IS NULL
        """
        return self.execute_query(query) 