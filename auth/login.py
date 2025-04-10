import bcrypt
import streamlit as st

# Credenciais do usuário master (em produção, isso deveria estar em um banco de dados)
USUARIO_MASTER = "Vinicius"
SENHA_MASTER = "V1n1c1u5@#"

def get_hashed_password(plain_text_password):
    """Gera um hash da senha usando bcrypt"""
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())

def check_password(usuario, senha):
    """Verifica se o usuário e senha estão corretos"""
    if usuario == USUARIO_MASTER:
        # Em produção, você compararia com o hash armazenado
        return senha == SENHA_MASTER
    return False

def init_session_state():
    """Inicializa o estado da sessão"""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None 