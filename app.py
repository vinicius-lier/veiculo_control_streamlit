import streamlit as st
from database import verify_user, init_db
from utils import check_login
from redis_client import save_data, get_data

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializa o banco de dados
init_db()

# Inicializa o estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# Função para fazer login
def login(username, password):
    success, user = verify_user(username, password)
    if success:
        st.session_state.logged_in = True
        st.session_state.username = user['username']
        st.session_state.role = user['role']
        # Salva os dados do usuário no Redis
        save_data(f"user_{username}", user)
        return True
    return False

# Função para fazer logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# Título da página
st.title("Sistema de Gestão de Veículos")

# Se não estiver logado, mostra o formulário de login
if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if login(username, password):
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
else:
    # Botões na parte superior
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1,1,1,1,1,1,1])
    
    with col1:
        if st.button("Dashboard"):
            st.switch_page("pages/dashboard.py")
    
    with col2:
        if st.button("Registrar Saída"):
            st.switch_page("pages/registrar_saida.py")
    
    with col3:
        if st.button("Registrar Retorno"):
            st.switch_page("pages/registrar_retorno.py")
    
    with col4:
        if st.button("Gerenciar Veículos"):
            st.switch_page("pages/gerenciar_veiculos.py")
    
    with col5:
        if st.button("Gerenciar Condutores"):
            st.switch_page("pages/gerenciar_condutores.py")
    
    with col6:
        if st.button("Gerenciar Usuários"):
            st.switch_page("pages/gerenciar_usuarios.py")
    
    with col7:
        if st.button("Sair"):
            logout()
    
    # Mostra informações do usuário
    st.write(f"Usuário: {st.session_state.username}")
    st.write(f"Função: {st.session_state.role}")
    
    # Tenta recuperar dados do usuário do Redis
    user_data = get_data(f"user_{st.session_state.username}")
    if user_data:
        st.write("Dados do usuário recuperados do Redis:")
        st.json(user_data) 