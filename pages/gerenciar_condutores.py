import streamlit as st
from database import register_driver, get_all_drivers, get_driver
from utils import check_login, save_uploaded_file
import os

# Configuração da página
st.set_page_config(
    page_title="Gerenciar Condutores - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Gerenciar Condutores")

# Formulário para cadastro de novo condutor
st.write("### Cadastrar Novo Condutor")
with st.form("driver_form"):
    nome = st.text_input("Nome Completo")
    cnh = st.text_input("Número da CNH")
    categoria = st.selectbox("Categoria da CNH", ["A", "B", "AB", "AC", "AD", "AE"])
    validade = st.date_input("Validade da CNH")
    foto_cnh = st.file_uploader("Foto da CNH", type=["jpg", "jpeg", "png"])
    
    submit = st.form_submit_button("Cadastrar Condutor")
    
    if submit:
        if not all([nome, cnh, categoria, validade, foto_cnh]):
            st.error("Todos os campos são obrigatórios")
        else:
            # Salvar foto da CNH
            foto_path = save_uploaded_file(foto_cnh, folder="imagens/cnh")
            
            # Preparar dados
            driver_data = {
                "nome": nome,
                "cnh": cnh,
                "categoria": categoria,
                "validade": validade.isoformat(),
                "foto_cnh": foto_path
            }
            
            # Registrar condutor
            driver_id = register_driver(driver_data)
            st.success(f"Condutor cadastrado com sucesso! ID: {driver_id}")

# Lista de condutores cadastrados
st.write("### Condutores Cadastrados")
drivers = get_all_drivers()

if not drivers:
    st.info("Não há condutores cadastrados.")
else:
    for driver_id, driver in drivers.items():
        with st.expander(f"{driver['name']} - CNH: {driver['document']}"):
            st.write(f"**Categoria:** {driver['categoria']}")
            st.write(f"**Validade:** {driver['validade']}")
            if os.path.exists(driver['foto_cnh']):
                st.image(driver['foto_cnh'], caption="Foto da CNH")
            else:
                st.warning("Foto da CNH não encontrada") 