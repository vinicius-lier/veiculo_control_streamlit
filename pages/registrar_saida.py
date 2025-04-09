import streamlit as st
from database import register_vehicle_exit, get_all_drivers, check_driver_has_active_vehicle
from utils import check_login, save_uploaded_file

# Configuração da página
st.set_page_config(
    page_title="Registrar Saída - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Registrar Saída de Veículo")

# Buscar condutores cadastrados
drivers = get_all_drivers()

if not drivers:
    st.error("Não há condutores cadastrados. Por favor, cadastre um condutor primeiro.")
    st.stop()

# Formulário de registro
with st.form("exit_form"):
    # Selecionar condutor
    driver_options = {f"{v['name']} - CNH: {v['document']}": k for k, v in drivers.items()}
    selected_driver = st.selectbox("Selecione o Condutor", options=list(driver_options.keys()))
    driver_id = driver_options[selected_driver]
    
    # Verificar se o condutor já tem veículo em uso
    if check_driver_has_active_vehicle(driver_id):
        st.error("Este condutor já possui um veículo em uso")
        st.stop()
    
    # Placa do veículo
    vehicle_plate = st.text_input("Placa do Veículo")
    
    # Destino
    destination = st.text_input("Destino")
    
    # Botão de submit
    submitted = st.form_submit_button("Registrar Saída")
    
    if submitted:
        if not all([vehicle_plate, destination]):
            st.error("Todos os campos são obrigatórios")
        else:
            # Preparar dados
            data = {
                "driver_id": driver_id,
                "vehicle_plate": vehicle_plate,
                "destination": destination
            }
            
            # Registrar saída
            exit_id, message = register_vehicle_exit(data)
            if exit_id:
                st.success(message)
            else:
                st.error(message) 