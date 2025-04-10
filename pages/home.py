import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db import get_connection
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Controle de Veículos",
    page_icon="🏍️",
    layout="wide"
)

# Verificar autenticação
if 'autenticado' not in st.session_state or not st.session_state.autenticado:
    st.switch_page("app.py")

# Título da página
st.title("🏍️ Dashboard - Controle de Veículos")

# Criar colunas para os cards
col1, col2, col3 = st.columns(3)

# Função para obter estatísticas
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total de veículos disponíveis
    cursor.execute("SELECT COUNT(*) FROM veiculos WHERE status = 'disponivel'")
    veiculos_disponiveis = cursor.fetchone()[0]
    
    # Total de veículos em uso
    cursor.execute("SELECT COUNT(*) FROM veiculos WHERE status = 'em uso'")
    veiculos_em_uso = cursor.fetchone()[0]
    
    # Total de condutores ativos
    cursor.execute("SELECT COUNT(DISTINCT condutor_id) FROM registros WHERE data_entrada IS NULL")
    condutores_ativos = cursor.fetchone()[0]
    
    conn.close()
    return veiculos_disponiveis, veiculos_em_uso, condutores_ativos

# Função para obter top 5 condutores
def get_top_condutores():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT c.nome, SUM(r.km_entrada - r.km_saida) as total_km
    FROM registros r
    JOIN condutores c ON r.condutor_id = c.id
    WHERE r.km_entrada IS NOT NULL
    GROUP BY c.id, c.nome
    ORDER BY total_km DESC
    LIMIT 5
    """)
    
    resultados = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame(resultados, columns=['Condutor', 'Quilometragem Total'])

# Função para obter histórico recente
def get_historico_recente():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        c.nome as condutor,
        v.placa,
        r.data_saida,
        r.data_entrada,
        r.km_saida,
        r.km_entrada
    FROM registros r
    JOIN condutores c ON r.condutor_id = c.id
    JOIN veiculos v ON r.veiculo_id = v.id
    ORDER BY r.data_saida DESC
    LIMIT 10
    """)
    
    resultados = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(resultados, columns=['Condutor', 'Placa', 'Data Saída', 'Data Entrada', 'KM Saída', 'KM Entrada'])
    df['Data Saída'] = pd.to_datetime(df['Data Saída']).dt.strftime('%d/%m/%Y %H:%M')
    df['Data Entrada'] = pd.to_datetime(df['Data Entrada']).dt.strftime('%d/%m/%Y %H:%M')
    return df

# Exibir cards com estatísticas
veiculos_disponiveis, veiculos_em_uso, condutores_ativos = get_stats()

with col1:
    st.metric("Veículos Disponíveis", veiculos_disponiveis)
with col2:
    st.metric("Veículos em Uso", veiculos_em_uso)
with col3:
    st.metric("Condutores Ativos", condutores_ativos)

# Top 5 condutores
st.subheader("Top 5 Condutores por Quilometragem")
df_top_condutores = get_top_condutores()
fig = px.bar(df_top_condutores, x='Condutor', y='Quilometragem Total',
             title='Quilometragem Total por Condutor')
st.plotly_chart(fig, use_container_width=True)

# Histórico recente
st.subheader("Histórico Recente de Saídas/Entradas")
df_historico = get_historico_recente()
st.dataframe(df_historico, use_container_width=True) 