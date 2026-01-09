import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Gestão NPS - Labor Engenharia", layout="wide")

# Estilo e Logo
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros Estratégicos")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Leitura e Limpeza Profunda
    df_raw = conn.read(ttl=0)
    
    # Criamos uma cópia limpa apenas com o que é data válida
    df = df_raw.copy()
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data']) # Remove qualquer linha que não tenha data válida
    
    if df.empty:
        st.warning("A planilha parece estar vazia ou sem datas válidas. Registre uma pesquisa para visualizar.")
    else:
        # Criar colunas de suporte garantindo que sejam números
        df['ano'] = df['data'].dt.year.fillna(0).astype(int)
        df['mes_nome'] = df['data'].dt.strftime('%m - %B')

        # --- FILTROS LATERAIS ---
        lista_empresas = ["Todas"] + sorted([str(e) for e in df['empresa'].unique() if e])
        empresa_sel = st.sidebar.selectbox("Filtrar por Empresa", lista_empresas)

        lista_anos = ["Todos"] + sorted(df['ano'].unique().astype(str).tolist())
        ano_sel = st.sidebar.selectbox("Filtrar por Ano", lista_anos)

        # Filtro de Indicador para o Gráfico de Evolução
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

        # --- DASHBOARD ---
        st.title("📊 Indicadores Labor Engenharia")
        
        if not df_filtrado.empty:
            # Métricas
            total = len(df_filtrado)
            # Garante que nota seja número para o cálculo
            df_filtrado['nota'] = pd.to_numeric(df_filtrado['nota'], errors='coerce').fillna(0)
            
            promotores = len(df_filtrado[df_filtrado['nota'] >= 9])
            detratores = len(df_filtrado[df_filtrado['nota'] <= 6])
            nps = ((promotores - detratores) / total * 100) if total > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Respostas no Período", total)
            m2.metric("NPS do Filtro", f"{nps:.1f}")
            m3.metric("Média Geral", f"{df_filtrado['nota'].mean():.1f}")

            st.divider()

            # --- GRÁFICO DE EVOLUÇÃO ---
            st.subheader(f"📈 Tendência: {analise_sel}")
            
            map_qualitativo = {"Péssimo": 1, "Ruim": 2, "Regular": 3, "Bom": 4, "Excelente": 5}
            df_plot = df_filtrado.copy()
            
            if coluna_analise != "nota":
                df_plot['valor_grafico'] = df_plot[coluna_analise].map(map_qualitativo).fillna(0)
                range_y = [0, 5.5]
            else:
                df_plot['valor_grafico'] = df_plot['nota']
                range_y = [0, 11]

            # Agrupar por dia (usando apenas a data sem hora para evitar conflitos)
            df_evolucao = df_plot.groupby(df_plot['data'].dt.date)['valor_grafico'].mean().reset_index()
            df_evolucao.columns = ['Data', 'Média']
            
            fig = px.line(df_evolucao, x='Data', y='Média', markers=True, line_shape="spline")
            fig.update_traces(line_color='#f37021', line_width=3)
            fig.update_layout(yaxis_range=range_y)
            st.plotly_chart(fig, use_container_width=True)

            # --- PIZZAS ---
            st.subheader("🎯 Detalhes por Indicador")
            ind_list = ["clareza", "prazos", "comunicacao", "atendimento", "custo"]
            cols_p = st.columns(5)
            for idx, c_db in enumerate(ind_list):
                if c_db in df_filtrado.columns:
                    with cols_p[idx]:
                        fig_p = px.pie(df_filtrado, names=c_db, title=c_db.capitalize(), hole=0.3)
                        fig_p.update_layout(showlegend=False)
                        st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado para os filtros selecionados.")

except Exception as e:
    st.error(f"Erro ao processar dados da planilha: {e}")
    st.info("Dica: Verifique se não existem linhas vazias entre os dados na sua planilha do Google.")
