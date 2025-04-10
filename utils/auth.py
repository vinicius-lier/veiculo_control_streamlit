import streamlit as st
import hashlib
import logging
from typing import Optional, Tuple
from utils.database import Database
from utils.validators import validar_senha, validar_email
from utils.constants import (
    ERRO_SENHA_INVALIDA,
    ERRO_EMAIL_INVALIDO,
    ERRO_USUARIO_NAO_ENCONTRADO,
    ERRO_SENHA_INCORRETA
)

logger = logging.getLogger(__name__)

class Auth:
    def __init__(self):
        self.db = Database()
        
    def _hash_senha(self, senha: str) -> str:
        """
        Gera o hash da senha.
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        return hashlib.sha256(senha.encode()).hexdigest()
        
    def login(self, email: str, senha: str) -> Tuple[bool, str]:
        """
        Realiza o login do usuário.
        
        Args:
            email: Email do usuário
            senha: Senha do usuário
            
        Returns:
            Tuple com (bool indicando sucesso, mensagem de erro)
        """
        try:
            # Valida email
            email_valido, msg_erro = validar_email(email)
            if not email_valido:
                return False, msg_erro
                
            # Busca usuário
            query = "SELECT * FROM usuarios WHERE email = ?"
            usuarios = self.db.execute_query(query, (email,))
            
            if not usuarios:
                return False, ERRO_USUARIO_NAO_ENCONTRADO
                
            usuario = usuarios[0]
            senha_hash = self._hash_senha(senha)
            
            if senha_hash != usuario['senha']:
                return False, ERRO_SENHA_INCORRETA
                
            # Salva dados na sessão
            st.session_state['usuario_id'] = usuario['id']
            st.session_state['usuario_nome'] = usuario['nome']
            st.session_state['usuario_email'] = usuario['email']
            st.session_state['autenticado'] = True
            
            logger.info(f"Usuário {email} logado com sucesso")
            return True, ""
            
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            return False, str(e)
            
    def logout(self) -> None:
        """
        Realiza o logout do usuário.
        """
        for key in ['usuario_id', 'usuario_nome', 'usuario_email', 'autenticado']:
            if key in st.session_state:
                del st.session_state[key]
                
        logger.info("Usuário deslogado")
        
    def registrar_usuario(self, nome: str, email: str, senha: str) -> Tuple[bool, str]:
        """
        Registra um novo usuário.
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            senha: Senha do usuário
            
        Returns:
            Tuple com (bool indicando sucesso, mensagem de erro)
        """
        try:
            # Valida email
            email_valido, msg_erro = validar_email(email)
            if not email_valido:
                return False, msg_erro
                
            # Valida senha
            senha_valida, msg_erro = validar_senha(senha)
            if not senha_valida:
                return False, msg_erro
                
            # Verifica se email já existe
            query = "SELECT * FROM usuarios WHERE email = ?"
            usuarios = self.db.execute_query(query, (email,))
            
            if usuarios:
                return False, "Email já cadastrado"
                
            # Insere usuário
            senha_hash = self._hash_senha(senha)
            query = "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)"
            self.db.execute_query(query, (nome, email, senha_hash))
            
            logger.info(f"Usuário {email} registrado com sucesso")
            return True, ""
            
        except Exception as e:
            logger.error(f"Erro no registro: {str(e)}")
            return False, str(e)
            
    def alterar_senha(self, senha_atual: str, nova_senha: str) -> Tuple[bool, str]:
        """
        Altera a senha do usuário.
        
        Args:
            senha_atual: Senha atual do usuário
            nova_senha: Nova senha do usuário
            
        Returns:
            Tuple com (bool indicando sucesso, mensagem de erro)
        """
        try:
            if 'usuario_id' not in st.session_state:
                return False, "Usuário não autenticado"
                
            # Valida nova senha
            senha_valida, msg_erro = validar_senha(nova_senha)
            if not senha_valida:
                return False, msg_erro
                
            # Verifica senha atual
            query = "SELECT senha FROM usuarios WHERE id = ?"
            usuarios = self.db.execute_query(query, (st.session_state['usuario_id'],))
            
            if not usuarios:
                return False, "Usuário não encontrado"
                
            senha_atual_hash = self._hash_senha(senha_atual)
            if senha_atual_hash != usuarios[0]['senha']:
                return False, "Senha atual incorreta"
                
            # Atualiza senha
            nova_senha_hash = self._hash_senha(nova_senha)
            query = "UPDATE usuarios SET senha = ? WHERE id = ?"
            self.db.execute_query(query, (nova_senha_hash, st.session_state['usuario_id']))
            
            logger.info(f"Senha do usuário {st.session_state['usuario_email']} alterada com sucesso")
            return True, ""
            
        except Exception as e:
            logger.error(f"Erro na alteração de senha: {str(e)}")
            return False, str(e)
            
    def verificar_autenticacao(self) -> bool:
        """
        Verifica se o usuário está autenticado.
        
        Returns:
            True se autenticado, False caso contrário
        """
        return st.session_state.get('autenticado', False)
        
    def get_usuario_atual(self) -> Optional[dict]:
        """
        Retorna os dados do usuário atual.
        
        Returns:
            Dicionário com os dados do usuário ou None se não autenticado
        """
        if not self.verificar_autenticacao():
            return None
            
        return {
            'id': st.session_state['usuario_id'],
            'nome': st.session_state['usuario_nome'],
            'email': st.session_state['usuario_email']
        } 