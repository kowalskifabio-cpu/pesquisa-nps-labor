import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Dashboard Labor Engenharia", layout="wide")

# Estilo e Logo
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros e Relatórios")

# Conexão com a planilha
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lê os dados
    df = conn.read(ttl=0)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)

    # --- FILTROS DE DATA ---
    min_date = df['data'].min().date()
    max_date = df['data'].max().date()
    data_sel = st.sidebar.date_input("Selecione o período", [min_date, max_date])

    if len(data_sel) == 2:
        df_filtrado = df[(df['data'].dt.date >= data_sel[0]) & (df['data'].dt.date <= data_sel[1])]
    else:
        df_filtrado = df

    # --- BOTÃO DE EXPORTAÇÃO EXCEL NA SIDEBAR ---
    st.sidebar.divider()
    st.sidebar.subheader("Exportar Dados")
    
    # Função para converter DataFrame para Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='NPS_Labor')
        return output.getvalue()

    excel_data = to_excel(df_filtrado)
    st.sidebar.download_button(
        label="📥 Baixar Relatório em Excel",
        data=excel_data,
        file_name=f'NPS_Labor_{datetime.now().strftime("%Y%m%d")}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # --- CONTEÚDO DO DASHBOARD ---
    st.title("📊 Indicadores de Pesquisa NPS")
    
    total_respostas = len(df_filtrado)
    promotores = len(df_filtrado[df_filtrado['nota'] >= 9])
    detratores = len(df_filtrado[df_filtrado['nota'] <= 6])
    nps = ((promotores - detratores) / total_respostas * 100) if total_respostas > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Pesquisas", total_respostas)
    m2.metric("NPS Geral", f"{nps:.1f}")
    m3.metric("Última Resposta", df_filtrado['data'].max().strftime('%d/%m/%Y'))

    st.divider()

    # --- EVOLUÇÃO (LINHA) ---
    st.subheader("📈 Evolução da Satisfação")
    df_linha = df_filtrado.groupby(df_filtrado['data'].dt.date)['nota'].mean().reset_index()
    fig_evolucao = px.line(df_linha, x='data', y='nota', markers=True, title="Média de Recomendação")
    fig_evolucao.update_traces(line_color='#f37021')
    st.plotly_chart(fig_evolucao, use_container_width=True)

    # --- INDICADORES (PIZZA) ---
    st.subheader("🍕 Distribuição por Indicador")
    indicadores = {
        "clareza": "Clareza Técnica",
        "prazos": "Prazos",
        "comunicacao": "Comunicação",
        "atendimento": "Atendimento",
        "custo": "Custo-benefício"
    }

    cols = st.columns(len(indicadores))
    for i, (col_nome, label) in enumerate(indicadores.items()):
        with cols[i]:
            fig_pizza = px.pie(df_filtrado, names=col_nome, title=label)
            fig_pizza.update_layout(showlegend=False)
            fig_pizza.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pizza, use_container_width=True)

    # --- TABELA DETALHADA ---
    st.divider()
    st.subheader("📋 Respostas Detalhadas")
    st.dataframe(df_filtrado.sort_values(by='data', ascending=False), use_container_width=True)

except Exception as e:
    st.warning("Aguardando dados para gerar o relatório.")
