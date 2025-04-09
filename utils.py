import streamlit as st
from datetime import datetime
import os
from database import verify_user

# Inicializa o estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

def save_uploaded_file(uploaded_file, folder="imagens/avarias"):
    """Salva um arquivo enviado pelo usuário"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def format_datetime(dt_str):
    """Formata uma string de data/hora para exibição"""
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%d/%m/%Y %H:%M")

def check_login():
    """Verifica se o usuário está logado"""
    if not st.session_state.logged_in:
        st.warning("Por favor, faça login para acessar esta página.")
        st.stop() 