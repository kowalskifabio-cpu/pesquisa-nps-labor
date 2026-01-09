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
    # 1. Leitura e Limpeza de Dados
    df_raw = conn.read(ttl=0)
    df = df_raw.copy()
    
    # Tratamento de datas
    df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['data']) 
    
    if df.empty:
        st.warning("Aguardando registros na planilha para exibir os indicadores.")
    else:
        # Criar colunas de tempo para os filtros
        df['ano'] = df['data'].dt.year.astype(int)
        df['mes_nome'] = df['data'].dt.strftime('%B')
        df['dia'] = df['data'].dt.day.astype(int)
        
        # Mapeamento de meses para português
        meses_dict = {
            "January": "Janeiro", "February": "Fevereiro", "March": "Março", 
            "April": "Abril", "May": "Maio", "June": "Junho", 
            "July": "Julho", "August": "Agosto", "September": "Setembro", 
            "October": "Outubro", "November": "Novembro", "December": "Dezembro"
        }
        df['mes_pt'] = df['mes_nome'].map(meses_dict)

        # --- FILTROS LATERAIS ---
        empresa_sel = st.sidebar.selectbox("1. Empresa", ["Todas"] + sorted([str(e) for e in df['empresa'].unique() if e]))
        ano_sel = st.sidebar.selectbox("2. Ano", ["Todos"] + sorted(df['ano'].unique().astype(str).tolist()))
        mes_sel = st.sidebar.selectbox("3. Mês", ["Todos"] + sorted(df['mes_pt'].unique().tolist()))
        dia_sel = st.sidebar.selectbox("4. Dia específico", ["Todos"] + sorted(df['dia'].unique().astype(str).tolist(), key=int))

        st.sidebar.divider()
        indicadores_map = {
            "Nota Geral (NPS)": "nota", "Clareza Técnica": "clareza", "Prazos": "prazos",
            "Comunicação": "comunicacao", "Atendimento": "atendimento", "Custo-benefício": "custo"
        }
        analise_sel = st.sidebar.selectbox("Ver evolução de:", list(indicadores_map.keys()))
        coluna_analise = indicadores_map[analise_sel]

        # --- APLICAÇÃO DOS FILTROS ---
        df_filtrado = df.copy()
        if empresa_sel != "Todas": df_filtrado = df_filtrado[df_filtrado['empresa'] == empresa_sel]
        if ano_sel != "Todos": df_filtrado = df_filtrado[df_filtrado['ano'] == int(ano_sel)]
        if mes_sel != "Todos": df_filtrado = df_filtrado[df_filtrado['mes_pt'] == mes_sel]
        if dia_sel != "Todos": df_filtrado = df_filtrado[df_filtrado['dia'] == int(dia_sel)]

        # --- BOTÃO EXPORTAR EXCEL ---
        def to_excel(df_to_save):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_to_save.to_excel(writer, index=False, sheet_name='Relatorio_NPS')
            return output.getvalue()

        st.sidebar.divider()
        st.sidebar.download_button(
            label="📥 Baixar Relatório Excel",
            data=to_excel(df_filtrado),
            file_name=f'NPS_Labor_{datetime.now().strftime("%d-%m-%Y")}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # --- DASHBOARD ---
        st.title("📊 Indicadores Labor Engenharia")
        
        if not df_filtrado.empty:
            # Métricas Principais
            total = len(df_filtrado)
            df_filtrado['nota'] = pd.to_numeric(df_filtrado['nota'], errors='coerce').fillna(0)
            nps = ((len(df_filtrado[df_filtrado['nota'] >= 9]) - len(df_filtrado[df_filtrado['nota'] <= 6])) / total * 100) if total > 0 else 0
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Respostas", total)
            c2.metric("NPS", f"{nps:.1f}")
            c3.metric("Média Geral", f"{df_filtrado['nota'].mean():.1f}")

            st.divider()

            # --- GRÁFICO DE EVOLUÇÃO ---
            st.subheader(f"📈 Tendência: {analise_sel}")
            map_qual = {"Péssimo": 1, "Ruim": 2, "Regular": 3, "Bom": 4, "Excelente": 5}
            df_plot = df_filtrado.copy()
            
            if coluna_analise != "nota":
                df_plot['valor'] = df_plot[coluna_analise].map(map_qual).fillna(0)
                r_y = [0, 5.5]
            else:
                df_plot['valor'] = df_plot['nota']
                r_y = [0, 11]

            df_ev = df_plot.groupby(df_plot['data'].dt.date)['valor'].mean().reset_index()
            fig = px.line(df_ev, x='data', y='valor', markers=True, line_shape="spline")
            fig.update_traces(line_color='#f37021', line_width=3)
            fig.update_layout(yaxis_range=r_y, xaxis_title="Data", yaxis_title="Média")
            st.plotly_chart(fig, use_container_width=True)

            # --- GRÁFICOS DE PIZZA ---
            st.subheader("🎯 Detalhes por Indicador")
            ind_list = ["clareza", "prazos", "comunicacao", "atendimento", "custo"]
            cols_p = st.columns(5)
            for idx, c_db in enumerate(ind_list):
                with cols_p[idx]:
                    fig_p = px.pie(df_filtrado, names=c_db, title=c_db.capitalize(), hole=0.3)
                    fig_p.update_layout(showlegend=False)
                    st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado para os filtros selecionados.")

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
