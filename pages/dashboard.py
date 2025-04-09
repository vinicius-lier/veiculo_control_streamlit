import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_driver_statistics
from utils import check_login

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Sistema de Gestão de Veículos",
    page_icon="📊",
    layout="wide"
)

# Verificar login
check_login()

# Título da página
st.title("Dashboard de Estatísticas")

# Obter estatísticas
stats = get_driver_statistics()

# Criar colunas para os gráficos
col1, col2 = st.columns(2)

# Gráfico de motoristas com mais saídas
with col1:
    st.subheader("Motoristas com Mais Saídas")
    if stats['most_exits']:
        df_exits = pd.DataFrame(stats['most_exits'])
        fig_exits = px.bar(df_exits, x='name', y='total_saidas', 
                          title="Número de Saídas por Motorista",
                          labels={'name': 'Motorista', 'total_saidas': 'Total de Saídas'})
        st.plotly_chart(fig_exits, use_container_width=True)
    else:
        st.info("Não há dados de saídas registradas.")

# Gráfico de motoristas com maior quilometragem
with col2:
    st.subheader("Motoristas com Maior Quilometragem")
    if stats['most_km']:
        df_km = pd.DataFrame(stats['most_km'])
        fig_km = px.bar(df_km, x='name', y='total_km', 
                        title="Quilometragem Total por Motorista",
                        labels={'name': 'Motorista', 'total_km': 'Quilometragem Total (km)'})
        st.plotly_chart(fig_km, use_container_width=True)
    else:
        st.info("Não há dados de quilometragem registrados.")

# Gráfico de motoristas com maior tempo de uso
st.subheader("Motoristas com Maior Tempo de Uso")
if stats['most_time']:
    df_time = pd.DataFrame(stats['most_time'])
    fig_time = px.bar(df_time, x='name', y='total_horas', 
                      title="Tempo Total de Uso por Motorista",
                      labels={'name': 'Motorista', 'total_horas': 'Tempo Total (horas)'})
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("Não há dados de tempo de uso registrados.")

# Tabela com os top 5 motoristas em cada categoria
st.subheader("Top 5 Motoristas")
col3, col4, col5 = st.columns(3)

with col3:
    st.write("**Mais Saídas**")
    if stats['most_exits']:
        df_exits = pd.DataFrame(stats['most_exits']).head(5)
        st.dataframe(df_exits[['name', 'total_saidas']], hide_index=True)
    else:
        st.info("Sem dados")

with col4:
    st.write("**Maior Quilometragem**")
    if stats['most_km']:
        df_km = pd.DataFrame(stats['most_km']).head(5)
        st.dataframe(df_km[['name', 'total_km']], hide_index=True)
    else:
        st.info("Sem dados")

with col5:
    st.write("**Maior Tempo de Uso**")
    if stats['most_time']:
        df_time = pd.DataFrame(stats['most_time']).head(5)
        st.dataframe(df_time[['name', 'total_horas']], hide_index=True)
    else:
        st.info("Sem dados") 