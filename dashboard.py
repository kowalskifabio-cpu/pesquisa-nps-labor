import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão NPS - Labor Engenharia", layout="wide")

# Estilo Laranja Labor
st.markdown("<style>.stMetric {background-color: #fdf2e9; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# Logo e Título na Sidebar
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros Estratégicos")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Carregamento de dados
    df = conn.read(ttl=0)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data'])

    # Criar colunas de suporte para filtros de tempo
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.strftime('%m - %B')

    # --- FILTROS NA SIDEBAR ---
    
    # 1. Filtro por Empresa
    lista_empresas = ["Todas"] + sorted(df['empresa'].unique().tolist())
    empresa_sel = st.sidebar.selectbox("Filtrar por Empresa", lista_empresas)

    # 2. Filtro por Ano
    lista_anos = ["Todos"] + sorted(df['ano'].unique().astype(str).tolist())
    ano_sel = st.sidebar.selectbox("Filtrar por Ano", lista_anos)

    # 3. Filtro por Mês
    lista_meses = ["Todos"] + sorted(df['mes'].unique().tolist())
    mes_sel = st.sidebar.selectbox("Filtrar por Mês", lista_meses)

    # --- NOVO FILTRO: INDICADOR PARA O GRÁFICO DE EVOLUÇÃO ---
    st.sidebar.divider()
    st.sidebar.subheader("Análise do Gráfico")
    indicadores_map = {
        "Nota Geral (NPS)": "nota",
        "Clareza Técnica": "clareza",
        "Prazos": "prazos",
        "Comunicação": "comunicacao",
        "Atendimento": "atendimento",
        "Custo-benefício": "custo"
    }
    analise_sel = st.sidebar.selectbox("Visualizar evolução de:", list(indicadores_map.keys()))
    coluna_analise = indicadores_map[analise_sel]

    # Aplicação dos Filtros de Dados
    df_filtrado = df.copy()
    if empresa_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['empresa'] == empresa_sel]
    if ano_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['ano'] == int(ano_sel)]
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes_sel]

    # --- DASHBOARD ---
    st.title(f"📊 Dashboard Labor Engenharia")
    if empresa_sel != "Todas":
        st.caption(f"Visualizando dados exclusivos da empresa: **{empresa_sel}**")
    
    # Métricas de Performance
    total = len(df_filtrado)
    promotores = len(df_filtrado[df_filtrado['nota'] >= 9]) if total > 0 else 0
    detratores = len(df_filtrado[df_filtrado['nota'] <= 6]) if total > 0 else 0
    nps = ((promotores - detratores) / total * 100) if total > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Respostas", total)
    m2.metric("NPS Geral", f"{nps:.1f
