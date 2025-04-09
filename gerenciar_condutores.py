import streamlit as st
import os
from database import register_driver, get_all_drivers
from utils import save_uploaded_file, check_login

def show():
    check_login()
    
    st.title("Gerenciamento de Condutores")
    
    # Formulário para cadastro de novo condutor
    with st.form("cadastro_condutor"):
        st.subheader("Cadastrar Novo Condutor")
        nome = st.text_input("Nome")
        cnh = st.text_input("CNH")
        categoria = st.selectbox("Categoria", ["A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"])
        validade = st.date_input("Validade da CNH")
        foto_cnh = st.file_uploader("Foto da CNH", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("Cadastrar"):
            try:
                driver_data = {
                    'nome': nome,
                    'cnh': cnh,
                    'categoria': categoria,
                    'validade': validade.isoformat()
                }
                
                if foto_cnh:
                    file_path = save_uploaded_file(foto_cnh, "cnh_photos")
                    driver_data['foto_cnh'] = file_path
                
                driver_id = register_driver(driver_data)
                st.success("Condutor cadastrado com sucesso!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar condutor: {e}")
    
    # Lista de condutores cadastrados
    st.subheader("Condutores Cadastrados")
    drivers = get_all_drivers()
    
    for driver in drivers:
        with st.expander(f"{driver['name']} - CNH: {driver['document']}"):
            st.write(f"**Nome:** {driver['name']}")
            st.write(f"**CNH:** {driver['document']}")
            st.write(f"**Categoria:** {driver['license_category']}")
            st.write(f"**Validade:** {driver['license_expiration']}")
            if 'license_photo_path' in driver and os.path.exists(driver['license_photo_path']):
                st.image(driver['license_photo_path'], caption="Foto da CNH")
            st.write(f"**Status:** {driver['status']}") 