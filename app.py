import streamlit as st
from auth.login import check_password

# Configuração da página
st.set_page_config(
    page_title="Controle de Veículos",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Desabilitar a barra lateral
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
""", unsafe_allow_html=True)

# Verificar se o usuário está autenticado
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🏍️ Sistema de Controle de Veículos")
    
    # Formulário de login
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if check_password(usuario, senha):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
else:
    # Redirecionar para a página home
    st.switch_page("pages/home.py") 