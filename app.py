import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Labor Engenharia - Pesquisa NPS", page_icon="🛡️")

# Estilo Laranja Labor
st.markdown("""
    <style>
    .stButton>button { background-color: #f37021; color: white; border-radius: 8px; width: 100%; font-weight: bold; border: none; }
    div[data-baseweb="slider"] > div > div { background-color: #f37021; }
    </style>
    """, unsafe_allow_html=True)

# Logo
try:
    st.image("logo.png", width=220)
except:
    st.title("Labor Engenharia")

st.title("Sua opinião é fundamental")

# Perguntas
nota = st.select_slider("Em uma escala de 0 a 10, recomendaria a Labor Engenharia?", options=list(range(11)), value=10)
feedback = st.text_area("O que motivou sua nota?")

st.divider()
st.subheader("Avaliação de Pontos-Chave")
opcoes = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]
p1 = st.select_slider("Clareza das orientações", options=opcoes, value="Excelente")
p2 = st.select_slider("Cumprimento de prazos", options=opcoes, value="Excelente")
p3 = st.select_slider("Comunicação", options=opcoes, value="Excelente")
p4 = st.select_slider("Atendimento e suporte", options=opcoes, value="Excelente")
p5 = st.select_slider("Custo-benefício", options=opcoes, value="Excelente")

st.divider()
contato = st.radio("Autoriza nosso contato para melhorias?", ["Sim", "Não"], index=1)

# Botão de Envio
if st.button("Enviar Avaliação"):
    try:
        # Tenta conectar
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Prepara a nova linha como um DataFrame (tabela)
        nova_linha = pd.DataFrame([{
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "nota": nota,
            "feedback": feedback,
            "clareza": p1,
            "prazos": p2,
            "comunicacao": p3,
            "atendimento": p4,
            "custo": p5,
            "contato": contato
        }])
        
        # Tenta ler a planilha. Se falhar (vazia), df_final é apenas a nova_linha
        try:
            df_atual = conn.read(ttl=0)
            if df_atual is not None and not df_atual.empty:
                df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            else:
                df_final = nova_linha
        except:
            df_final = nova_linha
        
        # Limpa colunas vazias que o Sheets às vezes cria
        df_final = df_final.dropna(axis=1, how='all')
        
        # Envia para a planilha
        conn.update(data=df_final)
        
        st.balloons()
        st.success("Agradecemos seu tempo e sua parceria! Suas respostas serão analisadas pela nossa diretoria.")
        
    except Exception as e:
        st.error("Erro técnico ao salvar. Verifique se o e-mail 'streamlit-labor@...' foi adicionado como EDITOR na planilha.")
        st.info(f"Detalhe do erro: {e}")
