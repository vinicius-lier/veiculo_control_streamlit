import os
import shutil
from datetime import datetime
import sqlite3
from utils.common import logger

class BackupManager:
    def __init__(self, db_path='data/database.db', backup_dir='data/backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Garante que o diretório de backup existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logger.info(f"Diretório de backup criado: {self.backup_dir}")
    
    def _get_backup_filename(self):
        """Gera nome do arquivo de backup com timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"backup_{timestamp}.db"
    
    def create_backup(self):
        """Cria um backup do banco de dados"""
        try:
            # Verifica se o banco existe
            if not os.path.exists(self.db_path):
                logger.error(f"Banco de dados não encontrado: {self.db_path}")
                return False, "Banco de dados não encontrado"
            
            # Gera nome do arquivo de backup
            backup_file = os.path.join(self.backup_dir, self._get_backup_filename())
            
            # Cria backup
            shutil.copy2(self.db_path, backup_file)
            logger.info(f"Backup criado com sucesso: {backup_file}")
            
            # Remove backups antigos (mantém apenas os 5 mais recentes)
            self._cleanup_old_backups()
            
            return True, f"Backup criado com sucesso: {backup_file}"
        except Exception as e:
            logger.error(f"Erro ao criar backup: {str(e)}")
            return False, f"Erro ao criar backup: {str(e)}"
    
    def _cleanup_old_backups(self, keep=5):
        """Remove backups antigos, mantendo apenas os N mais recentes"""
        try:
            # Lista todos os backups
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('backup_')]
            backups.sort(reverse=True)
            
            # Remove backups excedentes
            for backup in backups[keep:]:
                os.remove(os.path.join(self.backup_dir, backup))
                logger.info(f"Backup antigo removido: {backup}")
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {str(e)}")
    
    def restore_backup(self, backup_file):
        """Restaura um backup específico"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            # Verifica se o backup existe
            if not os.path.exists(backup_path):
                logger.error(f"Backup não encontrado: {backup_path}")
                return False, "Backup não encontrado"
            
            # Verifica se é um arquivo SQLite válido
            try:
                conn = sqlite3.connect(backup_path)
                conn.close()
            except sqlite3.Error:
                logger.error(f"Arquivo de backup inválido: {backup_path}")
                return False, "Arquivo de backup inválido"
            
            # Restaura o backup
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Backup restaurado com sucesso: {backup_file}")
            
            return True, f"Backup restaurado com sucesso: {backup_file}"
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {str(e)}")
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('backup_')]
            backups.sort(reverse=True)
            
            backup_info = []
            for backup in backups:
                path = os.path.join(self.backup_dir, backup)
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path))
                
                backup_info.append({
                    'filename': backup,
                    'size': size,
                    'modified': modified,
                    'path': path
                })
            
            return True, backup_info
        except Exception as e:
            logger.error(f"Erro ao listar backups: {str(e)}")
            return False, f"Erro ao listar backups: {str(e)}" 