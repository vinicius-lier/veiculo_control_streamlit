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
    driver_options = {f"{v['nome']} - CNH: {v['cnh']}": k for k, v in drivers.items()}
    selected_driver = st.selectbox("Selecione o Condutor", options=list(driver_options.keys()))
    driver_id = driver_options[selected_driver]
    
    # Verificar se o condutor já tem veículo em uso
    if check_driver_has_active_vehicle(driver_id):
        st.error("Este condutor já possui um veículo em uso")
        st.stop()
    
    # Tipo de veículo
    tipo_veiculo = st.selectbox("Tipo de Veículo", ["Carro", "Moto"])
    
    # Odômetro
    odometro = st.number_input("Odômetro de Saída", min_value=0, step=1)
    
    # Check de avaria
    tem_avaria = st.checkbox("Veículo com avaria?")
    
    # Upload de foto (opcional)
    foto_avaria = None
    if tem_avaria:
        foto_avaria = st.file_uploader("Foto da Avaria", type=["jpg", "jpeg", "png"])
    
    # Botão de submit
    submitted = st.form_submit_button("Registrar Saída")
    
    if submitted:
        # Preparar dados
        data = {
            "driver_id": driver_id,
            "tipo_veiculo": tipo_veiculo,
            "odometro_saida": odometro,
            "tem_avaria": tem_avaria,
            "foto_avaria": None
        }
        
        # Salvar foto se houver
        if foto_avaria:
            data["foto_avaria"] = save_uploaded_file(foto_avaria)
        
        # Registrar saída
        exit_id, message = register_vehicle_exit(data)
        if exit_id:
            st.success(message)
        else:
            st.error(message) 