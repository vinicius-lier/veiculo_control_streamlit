import streamlit as st
import logging
from utils.auth import Auth
from utils.schema import criar_banco_dados
from utils.constants import TITULO_APP, ICONE_APP, TEMA_APP

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title=TITULO_APP,
    page_icon=ICONE_APP,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Configuração do tema
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {'#FFFFFF' if TEMA_APP == 'light' else '#0E1117'};
            color: {'#000000' if TEMA_APP == 'light' else '#FFFFFF'};
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    """
    Função principal do aplicativo.
    """
    try:
        # Cria o banco de dados se não existir
        criar_banco_dados()
        
        # Inicializa a autenticação
        auth = Auth()
        
        # Se não estiver autenticado, mostra a tela de login
        if not auth.verificar_autenticacao():
            st.title("Login")
            
            with st.form("login_form"):
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar")
                
                if submit:
                    sucesso, mensagem = auth.login(email, senha)
                    if sucesso:
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error(mensagem)
                        
            # Link para registro
            st.markdown("---")
            st.markdown("Não tem uma conta? Registre-se abaixo:")
            
            with st.form("registro_form"):
                nome = st.text_input("Nome")
                email = st.text_input("Email", key="email_registro")
                senha = st.text_input("Senha", type="password", key="senha_registro")
                submit = st.form_submit_button("Registrar")
                
                if submit:
                    sucesso, mensagem = auth.registrar_usuario(nome, email, senha)
                    if sucesso:
                        st.success("Registro realizado com sucesso! Faça login para continuar.")
                    else:
                        st.error(mensagem)
                        
        # Se estiver autenticado, mostra o menu lateral
        else:
            usuario = auth.get_usuario_atual()
            
            # Menu lateral
            with st.sidebar:
                st.title("Menu")
                st.markdown(f"Bem-vindo, {usuario['nome']}!")
                st.markdown("---")
                
                # Botão de logout
                if st.button("Sair"):
                    auth.logout()
                    st.rerun()
                    
            # Conteúdo principal
            st.title("Sistema de Controle de Veículos")
            st.markdown("""
                Utilize o menu lateral para navegar entre as funcionalidades do sistema:
                
                - **Dashboard**: Visualize estatísticas e informações gerais
                - **Cadastro de Condutores**: Gerencie os condutores
                - **Cadastro de Veículos**: Gerencie os veículos
                - **Registro de Saída**: Registre a saída de veículos
                - **Registro de Entrada**: Registre a entrada de veículos
            """)
            
    except Exception as e:
        logger.error(f"Erro na execução do aplicativo: {str(e)}")
        st.error("Ocorreu um erro ao executar o aplicativo. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 