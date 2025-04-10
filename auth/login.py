import streamlit as st
import sqlite3
import logging
from utils.common import logger
from utils.security import SecurityManager

# Inicializa o gerenciador de segurança
security_manager = SecurityManager()

def login():
    """Função para autenticar o usuário"""
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                # Busca o usuário no banco de dados
                cursor.execute(
                    "SELECT id, username, password, role FROM users WHERE username = ?",
                    (username,)
                )
                user = cursor.fetchone()
                
                if user and security_manager.verify_password(password, user[2]):
                    # Gera o token JWT
                    token_data = {
                        'user_id': user[0],
                        'username': user[1],
                        'role': user[3]
                    }
                    token = security_manager.generate_token(token_data)
                    
                    # Armazena os dados na sessão
                    st.session_state.authenticated = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.session_state.role = user[3]
                    st.session_state.token = token
                    
                    logger.info(f"Usuário {username} autenticado com sucesso")
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    logger.warning(f"Tentativa de login falhou para o usuário {username}")
                    st.error("Usuário ou senha inválidos")
                    
            except Exception as e:
                logger.error(f"Erro durante o login: {str(e)}")
                st.error("Erro ao realizar login. Tente novamente.")
            finally:
                if 'conn' in locals():
                    conn.close()

def logout():
    """Função para fazer logout do usuário"""
    if 'authenticated' in st.session_state:
        logger.info(f"Usuário {st.session_state.username} fez logout")
        
        # Limpa os dados da sessão
        for key in ['authenticated', 'user_id', 'username', 'role', 'token']:
            if key in st.session_state:
                del st.session_state[key]
                
        st.success("Logout realizado com sucesso!")
        st.rerun()

def check_auth():
    """Verifica se o usuário está autenticado"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("Por favor, faça login para acessar esta página")
        st.stop()
        
    # Valida o token da sessão
    if not security_manager.validate_session(st.session_state):
        logger.warning(f"Sessão inválida para o usuário {st.session_state.username}")
        logout()
        st.stop() 