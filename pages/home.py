import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
from utils.auth import Auth
from utils.database import Database
from utils.constants import TITULO_APP, ICONE_APP

# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title=f"{TITULO_APP} - Dashboard",
    page_icon=ICONE_APP,
    layout="wide"
)

def get_estatisticas_gerais(db: Database) -> dict:
    """
    Obtém estatísticas gerais do sistema.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        Dicionário com as estatísticas
    """
    try:
        # Total de condutores
        total_condutores = db.execute_query("SELECT COUNT(*) as total FROM condutores")[0]['total']
        
        # Total de veículos
        total_veiculos = db.execute_query("SELECT COUNT(*) as total FROM veiculos")[0]['total']
        
        # Veículos em uso
        veiculos_em_uso = db.execute_query("""
            SELECT COUNT(*) as total 
            FROM registros 
            WHERE data_entrada IS NULL
        """)[0]['total']
        
        # Total de registros no mês atual
        primeiro_dia_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        registros_mes = db.execute_query(f"""
            SELECT COUNT(*) as total 
            FROM registros 
            WHERE strftime('%Y-%m-%d', data_saida) >= ?
        """, (primeiro_dia_mes,))[0]['total']
        
        return {
            'total_condutores': total_condutores,
            'total_veiculos': total_veiculos,
            'veiculos_em_uso': veiculos_em_uso,
            'registros_mes': registros_mes
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas gerais: {str(e)}")
        return {
            'total_condutores': 0,
            'total_veiculos': 0,
            'veiculos_em_uso': 0,
            'registros_mes': 0
        }

def get_registros_por_dia(db: Database) -> pd.DataFrame:
    """
    Obtém o número de registros por dia nos últimos 30 dias.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        DataFrame com os registros por dia
    """
    try:
        data_inicial = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        registros = db.execute_query("""
            SELECT 
                strftime('%Y-%m-%d', data_saida) as data,
                COUNT(*) as total
            FROM registros
            WHERE strftime('%Y-%m-%d', data_saida) >= ?
            GROUP BY strftime('%Y-%m-%d', data_saida)
            ORDER BY data
        """, (data_inicial,))
        
        return pd.DataFrame(registros)
    except Exception as e:
        logger.error(f"Erro ao obter registros por dia: {str(e)}")
        return pd.DataFrame(columns=['data', 'total'])

def get_veiculos_mais_utilizados(db: Database) -> pd.DataFrame:
    """
    Obtém os veículos mais utilizados.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        DataFrame com os veículos mais utilizados
    """
    try:
        veiculos = db.execute_query("""
            SELECT 
                v.marca || ' ' || v.modelo as veiculo,
                v.placa,
                COUNT(r.id) as total_usos
            FROM veiculos v
            LEFT JOIN registros r ON v.id = r.veiculo_id
            GROUP BY v.id
            ORDER BY total_usos DESC
            LIMIT 5
        """)
        
        return pd.DataFrame(veiculos)
    except Exception as e:
        logger.error(f"Erro ao obter veículos mais utilizados: {str(e)}")
        return pd.DataFrame(columns=['veiculo', 'placa', 'total_usos'])

def get_condutores_mais_ativos(db: Database) -> pd.DataFrame:
    """
    Obtém os condutores mais ativos.
    
    Args:
        db: Instância do banco de dados
        
    Returns:
        DataFrame com os condutores mais ativos
    """
    try:
        condutores = db.execute_query("""
            SELECT 
                c.nome,
                COUNT(r.id) as total_usos
            FROM condutores c
            LEFT JOIN registros r ON c.id = r.condutor_id
            GROUP BY c.id
            ORDER BY total_usos DESC
            LIMIT 5
        """)
        
        return pd.DataFrame(condutores)
    except Exception as e:
        logger.error(f"Erro ao obter condutores mais ativos: {str(e)}")
        return pd.DataFrame(columns=['nome', 'total_usos'])

def main():
    """
    Função principal da página.
    """
    try:
        # Verifica autenticação
        auth = Auth()
        if not auth.verificar_autenticacao():
            st.switch_page("app.py")
            
        # Inicializa banco de dados
        db = Database()
        
        # Título
        st.title("Dashboard")
        
        # Estatísticas gerais
        estatisticas = get_estatisticas_gerais(db)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Condutores", estatisticas['total_condutores'])
            
        with col2:
            st.metric("Total de Veículos", estatisticas['total_veiculos'])
            
        with col3:
            st.metric("Veículos em Uso", estatisticas['veiculos_em_uso'])
            
        with col4:
            st.metric("Registros no Mês", estatisticas['registros_mes'])
            
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Registros por Dia")
            df_registros = get_registros_por_dia(db)
            if not df_registros.empty:
                fig = px.line(
                    df_registros,
                    x='data',
                    y='total',
                    title='Registros nos Últimos 30 Dias'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há registros para exibir")
                
        with col2:
            st.subheader("Veículos Mais Utilizados")
            df_veiculos = get_veiculos_mais_utilizados(db)
            if not df_veiculos.empty:
                fig = px.bar(
                    df_veiculos,
                    x='veiculo',
                    y='total_usos',
                    title='Top 5 Veículos Mais Utilizados',
                    text='total_usos'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Não há dados de veículos para exibir")
                
        # Condutores mais ativos
        st.subheader("Condutores Mais Ativos")
        df_condutores = get_condutores_mais_ativos(db)
        if not df_condutores.empty:
            fig = px.pie(
                df_condutores,
                values='total_usos',
                names='nome',
                title='Top 5 Condutores Mais Ativos'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados de condutores para exibir")
            
    except Exception as e:
        logger.error(f"Erro na página home: {str(e)}")
        st.error("Ocorreu um erro ao carregar a página. Por favor, tente novamente.")

if __name__ == "__main__":
    main() 