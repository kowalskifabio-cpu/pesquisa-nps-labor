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

# Logo e Filtros na Sidebar
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros Estratégicos")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Carregamento e Limpeza Rigorosa de Dados
    df = conn.read(ttl=0)
    
    # Converte coluna data e remove o que não for data válida para evitar o erro de comparação
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data']) # Remove linhas onde a data deu erro
    
    # Criar colunas de suporte para filtros
    df['ano'] = df['data'].dt.year.astype(int)
    df['mes_num'] = df['data'].dt.month
    df['mes_nome'] = df['data'].dt.strftime('%m - %B')

    # --- FILTROS LATERAIS ---
    lista_empresas = ["Todas"] + sorted(df['empresa'].unique().tolist())
    empresa_sel = st.sidebar.selectbox("Filtrar por Empresa", lista_empresas)

    lista_anos = ["Todos"] + sorted(df['ano'].unique().astype(str).tolist())
    ano_sel = st.sidebar.selectbox("Filtrar por Ano", lista_anos)

    lista_meses = ["Todos"] + sorted(df['mes_nome'].unique().tolist())
    mes_sel = st.sidebar.selectbox("Filtrar por Mês", lista_meses)

    st.sidebar.divider()
    indicadores_map = {
        "Nota Geral (NPS)": "nota",
        "Clareza Técnica": "clareza",
        "Prazos": "prazos",
        "Comunicação": "comunicacao",
        "Atendimento": "atendimento",
        "Custo-benefício": "custo"
    }
    analise_sel = st.sidebar.selectbox("Ver evolução de:", list(indicadores_map.keys()))
    coluna_analise = indicadores_map[analise_sel]

    # --- APLICAÇÃO DOS FILTROS ---
    df_filtrado = df.copy()
    if empresa_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['empresa'] == empresa_sel]
    if ano_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['ano'] == int(ano_sel)]
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['mes_nome'] == mes_sel]

    # --- DASHBOARD ---
    st.title("📊 Indicadores Labor Engenharia")
    
    # Métricas
    total = len(df_filtrado)
    if total > 0:
        promotores = len(df_filtrado[df_filtrado['nota'] >= 9])
        detratores = len(df_filtrado[df_filtrado['nota'] <= 6])
        nps = ((promotores - detratores) / total * 100)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Respostas", total)
        m2.metric("NPS Geral", f"{nps:.1f}")
        m3.metric("Promotores", promotores)
        m4.metric("Detratores", detratores)

        st.divider()

        # --- GRÁFICO DE EVOLUÇÃO ---
        st.subheader(f"📈 Tendência: {analise_sel}")
        
        mapeamento = {"Péssimo": 1, "Ruim": 2, "Regular": 3, "Bom": 4, "Excelente": 5}
        df_plot = df_filtrado.copy()
        
        if coluna_analise != "nota":
            df_plot['valor'] = df_plot[coluna_analise].map(mapeamento).fillna(0)
            range_y = [0, 5.5]
        else:
            df_plot['valor'] = pd.to_numeric(df_plot['nota'], errors='coerce').fillna(0)
            range_y = [0, 11]

        # Agrupar por dia para o gráfico
        df_evolucao = df_plot.groupby(df_plot['data'].dt.date)['valor'].mean().reset_index()
        fig = px.line(df_evolucao, x='data', y='valor', markers=True, line_shape="spline")
        fig.update_traces(line_color='#f37021', line_width=3)
        fig.update_layout(yaxis_range=range_y, yaxis_title="Média")
        st.plotly_chart(fig, use_container_width=True)

        # --- GRÁFICOS DE PIZZA ---
        st.subheader("🍕 Distribuição dos Indicadores")
        ind_list = ["clareza", "prazos", "comunicacao", "atendimento", "custo"]
        cols_pizza = st.columns(5)
        for idx, col_db in enumerate(ind_list):
            with cols_pizza[idx]:
                fig_p = px.pie(df_filtrado, names=col_db, title=col_db.capitalize(), hole=0.3)
                fig_p.update_layout(showlegend=False)
                st.plotly_chart(fig_p, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para os filtros aplicados.")

except Exception as e:
    st.error(f"Erro ao carregar indicadores: {e}")
