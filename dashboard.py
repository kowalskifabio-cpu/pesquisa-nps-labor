import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Gestão NPS - Labor Engenharia", layout="wide")

# Estilo Laranja Labor
st.markdown("<style>.stMetric {background-color: #fdf2e9; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# Logo e Filtros na Sidebar
st.sidebar.image("logo.png", width=150)
st.sidebar.title("Filtros Estratégicos")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # 1. Leitura e Limpeza de Dados
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    
    # Tratamento rigoroso de datas para evitar erros de comparação
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data']) 
    
    if df.empty:
        st.warning("Aguardando registros na planilha para exibir os indicadores.")
    else:
        # Criar colunas de tempo para os filtros
        df['ano'] = df['data'].dt.year.astype(int)
        df['mes_nome'] = df['data'].dt.strftime('%B')
        df['dia'] = df['data'].dt.day.astype(int)
        
        # Mapeamento de meses para tradução e ordenação
        meses_dict = {
            "January": "Janeiro", "February": "Fevereiro", "March": "Março", 
            "April": "Abril", "May": "Maio", "June": "Junho", 
            "July": "Julho", "August": "Agosto", "September": "Setembro", 
            "October": "Outubro", "November": "Novembro", "December": "Dezembro"
        }
        df['mes_pt'] = df['mes_nome'].map(meses_dict)

        # --- FILTROS LATERAIS ---
        
        # Filtro de Empresa
        lista_empresas = ["Todas"] + sorted([str(e) for e in df['empresa'].unique() if e])
        empresa_sel = st.sidebar.selectbox("1. Empresa", lista_empresas)

        # Filtro de Ano
        lista_anos = ["Todos"] + sorted(df['ano'].unique().astype(str).tolist())
        ano_sel = st.sidebar.selectbox("2. Ano", lista_anos)

        # FILTRO DE MÊS (Novo)
        lista_meses = ["Todos"] + sorted(df['mes_pt'].unique().tolist())
        mes_sel = st.sidebar.selectbox("3. Mês", lista_meses)

        # FILTRO DE DIA (Novo)
        lista_dias = ["Todos"] + sorted(df['dia'].unique().astype(str).tolist(), key=int)
        dia_sel = st.sidebar.selectbox("4. Dia específico", lista_dias)

        # Filtro de Indicador para o Gráfico
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
            df_filtrado = df_filtrado[df_filtrado['mes_pt'] == mes_sel]
        if dia_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['dia'] == int(dia_sel)]

        # --- DASHBOARD ---
        st.title("📊 Indicadores Labor Engenharia")
        
        if not df_filtrado.empty:
            # Métricas
            total = len(df_filtrado)
            df_filtrado['nota'] = pd.to_numeric(df_filtrado['nota'], errors='coerce').fillna(0)
            
            promotores = len(df_filtrado[df_filtrado['nota'] >= 9])
            detratores = len(df_filtrado[df_filtrado['nota'] <= 6])
            nps = ((promotores - detratores) / total * 100) if total > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Respostas Selecionadas", total)
            c2.metric("NPS do Filtro", f"{nps:.1f}")
            c3.metric("Média das Notas", f"{df_filtrado['nota'].mean():.1f}")

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

            # Agrupar por data para o gráfico de linha
            df_evolucao = df_plot.groupby(df_plot['data'].dt.date)['valor_grafico'].mean().reset_index()
            df_evolucao.columns = ['Data', 'Média']
            
            fig = px.line(df_evolucao, x='Data', y='Média', markers=True, line_shape="spline")
            fig.update_traces(line_color='#f37021', line_width=3)
            fig.update_layout(yaxis_range=range_y, xaxis_title="Data", yaxis_title="Média")
            st.plotly_chart(fig, use_container_width=True)

            # --- GRÁFICOS DE PIZZA ---
            st.subheader("🎯 Distribuição dos Indicadores")
            ind_list = ["clareza", "prazos", "comunicacao", "atendimento", "custo"]
            cols_p = st.columns(5)
            for idx, c_db in enumerate(ind_list):
                if c_db in df_filtrado.columns:
                    with cols_p[idx]:
                        fig_p = px.pie(df_filtrado, names=c_db, title=c_db.capitalize(), hole=0.3)
                        fig_p.update_layout(showlegend=False)
                        st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado para os filtros selecionados. Tente mudar o Mês ou o Dia.")

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
