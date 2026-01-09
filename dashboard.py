import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Dashboard Labor Engenharia", layout="wide")
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros e Relatórios")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=0)
    # Garante que 'data' seja tratada corretamente
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data'])

    # Filtros de Data
    min_date = df['data'].min().date()
    max_date = df['data'].max().date()
    data_sel = st.sidebar.date_input("Período", [min_date, max_date])

    if len(data_sel) == 2:
        df_filtrado = df[(df['data'].dt.date >= data_sel[0]) & (df['data'].dt.date <= data_sel[1])]
    else:
        df_filtrado = df

    # Exportar Excel
    def to_excel(df_to_save):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_to_save.to_excel(writer, index=False, sheet_name='NPS')
        return output.getvalue()

    st.sidebar.download_button("📥 Baixar Excel", to_excel(df_filtrado), "NPS_Labor.xlsx")

    # Métricas
    st.title("📊 Indicadores Labor Engenharia")
    total = len(df_filtrado)
    nps = ((len(df_filtrado[df_filtrado['nota'] >= 9]) - len(df_filtrado[df_filtrado['nota'] <= 6])) / total * 100) if total > 0 else 0
    
    c1, c2 = st.columns(2)
    c1.metric("Total de Pesquisas", total)
    c2.metric("NPS", f"{nps:.1f}")

    # Gráficos de Pizza
    st.subheader("🍕 Avaliação por Indicador")
    indicadores = ["clareza", "prazos", "comunicacao", "atendimento", "custo"]
    cols = st.columns(len(indicadores))
    
    for i, ind in enumerate(indicadores):
        if ind in df_filtrado.columns:
            with cols[i]:
                fig = px.pie(df_filtrado, names=ind, title=ind.capitalize())
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # Gráfico de Linha
    st.subheader("📈 Evolução")
    df_l = df_filtrado.groupby(df_filtrado['data'].dt.date)['nota'].mean().reset_index()
    st.plotly_chart(px.line(df_l, x='data', y='nota', markers=True).update_traces(line_color='#f37021'), use_container_width=True)

except Exception as e:
    st.info("Aguardando novas respostas compatíveis com a planilha.")
