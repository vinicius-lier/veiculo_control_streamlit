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
        exit_options = {f"{k} - {v['condutor']} ({v['tipo_veiculo']}) - {format_datetime(v['data_saida'])}": k 
                       for k, v in active_exits.items()}
        selected_exit = st.selectbox("Selecione o veículo", options=list(exit_options.keys()))
        exit_id = exit_options[selected_exit]
        
        # Odômetro
        odometro = st.number_input("Odômetro de Retorno", min_value=0, step=1)
        
        # Check de avaria
        tem_avaria = st.checkbox("Veículo com avaria no retorno?")
        
        # Botão de submit
        submitted = st.form_submit_button("Registrar Retorno")
        
        if submitted:
            # Preparar dados
            data = {
                "odometro_retorno": odometro,
                "tem_avaria_retorno": tem_avaria
            }
            
            # Registrar retorno
            success, message = register_vehicle_return(exit_id, data)
            if success:
                st.success(message)
            else:
                st.error(message) 