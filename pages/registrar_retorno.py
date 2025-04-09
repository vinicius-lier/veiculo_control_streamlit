import streamlit as st
from database import get_active_exits, register_vehicle_return
from utils import check_login, format_datetime

# Configuração da página
st.set_page_config(
    page_title="Registrar Retorno - Sistema de Gestão de Veículos",
    page_icon="🚗",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Registrar Retorno de Veículo")

# Buscar saídas ativas
active_exits = get_active_exits()

if not active_exits:
    st.info("Não há veículos em uso no momento.")
else:
    # Formulário de registro
    with st.form("return_form"):
        # Selecionar saída
        exit_options = {f"{k} - {v['vehicle_plate']} - {format_datetime(v['data_saida'])}": k 
                       for k, v in active_exits.items()}
        selected_exit = st.selectbox("Selecione o veículo", options=list(exit_options.keys()))
        exit_id = exit_options[selected_exit]
        
        # Odômetro
        odometro_inicial = st.number_input("Odômetro Inicial", min_value=0, step=1)
        odometro_final = st.number_input("Odômetro Final", min_value=odometro_inicial, step=1)
        quilometragem = odometro_final - odometro_inicial
        
        # Observações
        observacoes = st.text_area("Observações")
        
        # Botão de submit
        submitted = st.form_submit_button("Registrar Retorno")
        
        if submitted:
            # Preparar dados
            data = {
                "observations": observacoes,
                "quilometragem": quilometragem
            }
            
            # Registrar retorno
            success, message = register_vehicle_return(exit_id, data)
            if success:
                st.success(message)
            else:
                st.error(message) 