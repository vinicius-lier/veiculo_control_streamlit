import streamlit as st
from database import register_vehicle_exit, get_all_vehicles, get_all_drivers, init_db
from utils import check_login
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Registrar Saída - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
if not check_login():
    st.error("Por favor, faça login para acessar esta página")
    st.stop()

# Inicializar banco de dados
init_db()

# Título da página
st.title("Registrar Saída de Veículo")

# Buscar veículos e motoristas disponíveis
vehicles = get_all_vehicles()
drivers = get_all_drivers()

# Filtrar apenas veículos disponíveis
available_vehicles = {k: v for k, v in vehicles.items() if v['status'] == 'available'}

if not available_vehicles:
    st.warning("Não há veículos disponíveis para saída")
    st.stop()

if not drivers:
    st.warning("Não há motoristas cadastrados")
    st.stop()

# Formulário de saída
with st.form("vehicle_exit_form"):
    # Seleção do veículo
    vehicle_options = {f"{v['plate']} - {v['model']} ({v['year']})": k for k, v in available_vehicles.items()}
    selected_vehicle = st.selectbox(
        "Selecione o Veículo",
        options=list(vehicle_options.keys())
    )
    
    # Seleção do motorista
    driver_options = {f"{d['nome']} - CNH: {d['cnh']}": k for k, d in drivers.items()}
    selected_driver = st.selectbox(
        "Selecione o Motorista",
        options=list(driver_options.keys())
    )
    
    # Data/hora esperada de retorno
    min_date = datetime.now()
    max_date = min_date + timedelta(days=30)
    expected_return = st.date_input(
        "Data Prevista de Retorno",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=min_date.date()
    )
    
    # Quilometragem inicial
    initial_odometer = st.number_input("Quilometragem Inicial", min_value=0)
    
    # Destino e finalidade
    destination = st.text_input("Destino")
    purpose = st.text_area("Finalidade da Saída")
    
    # Checklist Externo
    st.subheader("Checklist Externo")
    external_checklist = {
        "farol": st.checkbox("Faróis"),
        "pneus": st.checkbox("Pneus"),
        "lataria": st.checkbox("Lataria"),
        "limpadores": st.checkbox("Limpadores"),
        "retrovisores": st.checkbox("Retrovisores"),
        "observacoes_externas": st.text_area("Observações Externas")
    }
    
    # Checklist Interno
    st.subheader("Checklist Interno")
    internal_checklist = {
        "cinto": st.checkbox("Cinto de Segurança"),
        "freio": st.checkbox("Freio"),
        "direcao": st.checkbox("Direção"),
        "cambio": st.checkbox("Câmbio"),
        "painel": st.checkbox("Painel"),
        "ar_condicionado": st.checkbox("Ar Condicionado"),
        "observacoes_internas": st.text_area("Observações Internas")
    }
    
    # Botão de envio
    submitted = st.form_submit_button("Registrar Saída")
    
    if submitted:
        if not destination:
            st.error("Por favor, informe o destino")
        elif not purpose:
            st.error("Por favor, informe a finalidade da saída")
        else:
            # Preparar dados
            exit_data = {
                "vehicle_id": vehicle_options[selected_vehicle],
                "driver_id": driver_options[selected_driver],
                "user_id": st.session_state.user_id,
                "expected_return_date": expected_return.isoformat(),
                "initial_odometer": initial_odometer,
                "destination": destination,
                "purpose": purpose,
                "external_checklist": external_checklist,
                "internal_checklist": internal_checklist
            }
            
            # Registrar saída
            exit_id, message = register_vehicle_exit(exit_data)
            
            if exit_id:
                st.success(message)
                st.balloons()
            else:
                st.error(message) 