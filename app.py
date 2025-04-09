import streamlit as st
from database import init_db, verify_user, create_user
from utils import init_session_state
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Veículos",
    page_icon="imagens\4.png",
    layout="wide"
)

# Inicialização
init_session_state()
init_db()

# Título principal
st.title("Sistema de Gestão de Veículos")

# Sidebar para navegação
if st.session_state.logged_in:
    st.sidebar.title("Menu")
    st.sidebar.write(f"Usuário: {st.session_state.username}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/gerenciar_condutores.py", label="Gerenciar Condutores")
    st.sidebar.page_link("pages/registrar_saida.py", label="Registrar Saída")
    st.sidebar.page_link("pages/registrar_retorno.py", label="Registrar Retorno")
    st.sidebar.page_link("pages/gerar_relatorio.py", label="Gerar Relatório")
else:
    # Formulário de login
    st.write("### Login")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            success, user = verify_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = user['username']
                st.session_state.user_role = user['role']
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    
    # Seção para criar novo usuário
    st.markdown("---")
    st.write("### Criar Novo Usuário")
    with st.form("create_user_form"):
        new_username = st.text_input("Nome de usuário")
        new_password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirmar senha", type="password")
        create = st.form_submit_button("Criar Usuário")
        
        if create:
            if new_password != confirm_password:
                st.error("As senhas não coincidem")
            else:
                success, message = create_user(new_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message) 