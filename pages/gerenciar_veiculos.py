import streamlit as st
from database import register_vehicle, get_all_vehicles
from utils import check_login

# Configuração da página
st.set_page_config(
    page_title="Gerenciar Veículos - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Gerenciar Veículos")

# Formulário para cadastro de novo veículo
st.write("### Cadastrar Novo Veículo")
with st.form("vehicle_form"):
    plate = st.text_input("Placa do Veículo").upper()
    vehicle_type = st.selectbox("Tipo de Veículo", ["Carro", "Moto"])
    model = st.text_input("Modelo")
    year = st.number_input("Ano", min_value=1900, max_value=2024, value=2024)
    
    submit = st.form_submit_button("Cadastrar Veículo")
    
    if submit:
        if not all([plate, vehicle_type, model, year]):
            st.error("Todos os campos são obrigatórios")
        else:
            # Preparar dados
            vehicle_data = {
                "plate": plate,
                "type": vehicle_type,
                "model": model,
                "year": year
            }
            
            # Registrar veículo
            vehicle_id, message = register_vehicle(vehicle_data)
            if vehicle_id:
                st.success(message)
            else:
                st.error(message)

# Lista de veículos cadastrados
st.write("### Veículos Cadastrados")
vehicles = get_all_vehicles()

if not vehicles:
    st.info("Não há veículos cadastrados.")
else:
    for vehicle_id, vehicle in vehicles.items():
        with st.expander(f"{vehicle['plate']} - {vehicle['model']} ({vehicle['year']})"):
            st.write(f"**Tipo:** {vehicle['type']}")
            st.write(f"**Status:** {vehicle['status']}") 