import streamlit as st
from database import get_all_users
from utils import check_login

# Verificar login
if not check_login():
    st.error("Por favor, faça login para acessar esta página")
    st.stop()

# Título da página
st.title("Usuários Cadastrados")

# Buscar usuários
users = get_all_users()

if not users:
    st.warning("Nenhum usuário cadastrado")
else:
    # Criar uma tabela com os usuários
    data = []
    for user in users.values():
        data.append({
            "Usuário": user['usuario'],
            "Nome": user['nome'],
            "Função": user['funcao'],
            "Email": user['email'] or "Não informado",
            "Criado em": user['criado_em'].split('T')[0] if user['criado_em'] else "N/A",
            "Último acesso": user['ultimo_acesso'].split('T')[0] if user['ultimo_acesso'] else "Nunca"
        })
    
    st.table(data)

# Nota de segurança
st.markdown("---")
st.info("⚠️ Por segurança, as senhas não são exibidas") 