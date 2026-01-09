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
    m2.metric("NPS Geral", f"{nps:.1f}")
    m3.metric("Promotores", f"{promotores}")
    m4.metric("Detratores", f"{detratores}")

    st.divider()

    # --- GRÁFICO DE EVOLUÇÃO DINÂMICO ---
    st.subheader(f"📈 Evolução: {analise_sel}")
    
    if not df_filtrado.empty:
        # Se for indicador (Péssimo a Excelente), precisamos converter para números para tirar média
        mapeamento_qualitativo = {"Péssimo": 1, "Ruim": 2, "Regular": 3, "Bom": 4, "Excelente": 5}
        
        df_plot = df_filtrado.copy()
        
        if coluna_analise != "nota":
            df_plot['valor_grafico'] = df_plot[coluna_analise].map(mapeamento_qualitativo)
            titulo_y = "Média (1=Péssimo, 5=Excelente)"
            range_y = [0, 6]
        else:
            df_plot['valor_grafico'] = df_plot['nota']
            titulo_y = "Nota (0 a 10)"
            range_y = [0, 11]

        df_evolucao = df_plot.groupby(df_plot['data'].dt.date)['valor_grafico'].mean().reset_index()
        
        fig_linha = px.line(df_evolucao, x='data', y='valor_grafico', markers=True, 
                            title=f"Tendência de {analise_sel}",
                            line_shape="spline")
        
        fig_linha.update_traces(line_color='#f37021', line_width=4)
        fig_linha.update_layout(yaxis_title=titulo_y, yaxis_range=range_y)
        st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

    # --- INDICADORES (PIZZA) ---
    st.divider()
    st.subheader("🎯 Distribuição Geral dos Indicadores")
    indicadores_pizza = {"clareza": "Clareza", "prazos": "Prazos", "comunicacao": "Comunicação", 
                         "atendimento": "Suporte", "custo": "Custo"}
    
    cols = st.columns(len(indicadores_pizza))
    for i, (col_db, nome) in enumerate(indicadores_pizza.items()):
        if col_db in df_filtrado.columns:
            with cols[i]:
                fig_p = px.pie(df_filtrado, names=col_db, title=nome, hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_p.update_layout(showlegend=False)
                fig_p.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_p, use_container_width=True)

    # Exportação
    def export_excel(df_exp):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_exp.to_excel(writer, index=False)
        return output.getvalue()

    st.sidebar.divider()
    st.sidebar.download_button("📥 Exportar Dados Filtrados", export_excel(df_filtrado), "Relatorio_Labor.xlsx")

except Exception as e:
    st.error(f"Erro ao carregar indicadores: {e}")
