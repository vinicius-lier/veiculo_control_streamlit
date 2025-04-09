import streamlit as st
from database import verify_user, init_db, create_user
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
if 'show_register_form' not in st.session_state:
    st.session_state.show_register_form = False

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

# Função para mostrar/esconder o formulário de cadastro
def toggle_register_form():
    st.session_state.show_register_form = not st.session_state.show_register_form

# Título da página
st.title("Sistema de Gestão de Veículos")

# Se não estiver logado, mostra o formulário de login
if not st.session_state.logged_in:
    # Formulário de login
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        col1, col2 = st.columns([3, 1])
        with col1:
            submit = st.form_submit_button("Entrar")
        with col2:
            if st.form_submit_button("Criar Conta"):
                toggle_register_form()
        
        if submit:
            if login(username, password):
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    
    # Formulário de cadastro
    if st.session_state.show_register_form:
        st.markdown("---")
        st.subheader("Criar Nova Conta")
        with st.form("register_form"):
            new_username = st.text_input("Nome de usuário")
            new_name = st.text_input("Nome completo")
            new_email = st.text_input("E-mail (opcional)")
            new_password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirmar senha", type="password")
            col1, col2 = st.columns([3, 1])
            with col1:
                register = st.form_submit_button("Cadastrar")
            with col2:
                if st.form_submit_button("Cancelar"):
                    toggle_register_form()
            
            if register:
                if new_password != confirm_password:
                    st.error("As senhas não coincidem")
                else:
                    success, message = create_user(new_username, new_password, new_name, new_email)
                    if success:
                        st.success(message)
                        st.session_state.show_register_form = False
                    else:
                        st.error(message)
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