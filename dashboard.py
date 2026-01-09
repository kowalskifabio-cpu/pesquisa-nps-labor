import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard NPS - Labor Engenharia", layout="wide")

# Estilo e Logo
st.image("logo.png", width=200)
st.title("📊 Indicadores de Satisfação")

# Conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lê os dados (ttl=0 para ler sempre o mais atualizado)
    df = conn.read(ttl=0)
    
    # Converter a coluna 'data' para formato de data real
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)

    # --- FILTROS NA BARRA LATERAL ---
    st.sidebar.header("Filtros")
    data_inicio = st.sidebar.date_input("Data Inicial", df['data'].min())
    data_fim = st.sidebar.date_input("Data Final", df['data'].max())

    # Filtrar o DataFrame
    mask = (df['data'].dt.date >= data_inicio) & (df['data'].dt.date <= data_fim)
    df_filtrado = df.loc[mask]

    # --- MÉTRICAS PRINCIPAIS ---
    # Cálculo NPS: % Promotores (9-10) - % Detratores (0-6)
    promotores = len(df_filtrado[df_filtrado['nota'] >= 9])
    detratores = len(df_filtrado[df_filtrado['nota'] <= 6])
    total = len(df_filtrado)
    nps = ((promotores - detratores) / total * 100) if total > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Respostas", total)
    col2.metric("NPS Geral", f"{nps:.1f}")
    col3.metric("Promotores", f"{(promotores/total*100):.1f}%" if total > 0 else "0%")

    st.divider()

    # --- GRÁFICOS DE PIZZA (INDICADORES) ---
    st.subheader("Avaliação por Indicador")
    cols_indicadores = st.columns(3)
    
    indicadores = {
        "clareza": "Clareza Técnica",
        "prazos": "Prazos",
        "comunicacao": "Comunicação",
        "atendimento": "Atendimento",
        "custo": "Custo-benefício"
    }

    # Gerar um gráfico de pizza para cada indicador
    for i, (col_db, nome_exibicao) in enumerate(indicadores.items()):
        with cols_indicadores[i % 3]:
            fig = px.pie(df_filtrado, names=col_db, title=nome_exibicao, 
                         color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig, use_container_width=True)

    # --- GRÁFICO DE LINHA (EVOLUÇÃO) ---
    st.divider()
    st.subheader("Evolução das Notas no Tempo")
    df_evolucao = df_filtrado.groupby(df_filtrado['data'].dt.date)['nota'].mean().reset_index()
    fig_linha = px.line(df_evolucao, x='data', y='nota', title="Média de Recomendação por Dia",
                        markers=True, line_shape="spline")
    fig_linha.update_traces(line_color='#f37021') # Laranja Labor
    st.plotly_chart(fig_linha, use_container_width=True)

    # --- TABELA DE FEEDBACKS ---
    st.divider()
    st.subheader("Feedbacks Recentes")
    st.dataframe(df_filtrado[['data', 'empresa', 'nota', 'feedback']].sort_values(by='data', ascending=False))

except Exception as e:
    st.error("Aguardando as primeiras respostas para gerar os gráficos.")
    st.info("Certifique-se de que a planilha possui dados e os nomes das colunas estão corretos.")
