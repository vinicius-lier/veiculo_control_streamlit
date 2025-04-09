import streamlit as st
import os
from database import verify_user, init_db, create_user
from utils import check_login
from redis_client import save_data, get_data
import base64

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Função para carregar a logo
def load_logo():
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            return f"data:image/png;base64,{b64}"
    return None

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
    # Layout do login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        logo = load_logo()
        if logo:
            st.image(logo, width=200)
        
        st.title("Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                success, user = verify_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user['role']
                    st.experimental_rerun()
                else:
                    st.error("Usuário ou senha inválidos")
        
        # Botão de cadastro (apenas visível para o MASTER)
        if st.session_state.get('role') == 'master':
            if st.button("Cadastrar Novo Usuário"):
                st.session_state.show_register = True
        
        # Formulário de cadastro
        if st.session_state.get('show_register'):
            with st.form("register_form"):
                st.subheader("Cadastrar Novo Usuário")
                new_username = st.text_input("Nome de Usuário")
                new_password = st.text_input("Senha", type="password")
                new_name = st.text_input("Nome Completo")
                new_email = st.text_input("Email (opcional)")
                
                if st.form_submit_button("Cadastrar"):
                    success, message = create_user(
                        new_username, 
                        new_password, 
                        new_name, 
                        new_email,
                        {'role': st.session_state.role}
                    )
                    if success:
                        st.success(message)
                        st.session_state.show_register = False
                    else:
                        st.error(message)
else:
    # Menu principal
    st.sidebar.title("Menu")
    
    # Opções do menu
    menu_option = st.sidebar.radio(
        "Selecione uma opção:",
        ["Início", "Gerenciar Condutores", "Gerenciar Veículos", "Registrar Saída", "Registrar Retorno"]
    )
    
    # Logout
    if st.sidebar.button("Sair"):
        logout()
    
    # Conteúdo baseado na opção selecionada
    if menu_option == "Início":
        st.title("Bem-vindo ao Sistema de Gestão de Veículos")
        st.write(f"Usuário: {st.session_state.username}")
        
    elif menu_option == "Gerenciar Condutores":
        from pages.gerenciar_condutores import show as show_condutores
        show_condutores()
        
    elif menu_option == "Gerenciar Veículos":
        from pages.gerenciar_veiculos import show as show_veiculos
        show_veiculos()
        
    elif menu_option == "Registrar Saída":
        from pages.registrar_saida import show as show_saida
        show_saida()
        
    elif menu_option == "Registrar Retorno":
        from pages.registrar_retorno import show as show_retorno
        show_retorno()
    
    # Mostra informações do usuário
    st.write(f"Usuário: {st.session_state.username}")
    st.write(f"Função: {st.session_state.role}")
    
    # Tenta recuperar dados do usuário do Redis
    user_data = get_data(f"user_{st.session_state.username}")
    if user_data:
        st.write("Dados do usuário recuperados do Redis:")
        st.json(user_data) 