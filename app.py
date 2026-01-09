import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Labor Engenharia - Pesquisa NPS", page_icon="🛡️")

# --- ESTILO VISUAL (LARANJA LABOR) ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #f37021;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    div[data-baseweb="slider"] > div > div {
        background-color: #f37021;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
try:
    st.image("logo.png", width=220)
except:
    st.subheader("Labor Engenharia")

st.title("Sua opinião é fundamental")
st.write("A **Labor Engenharia** quer ouvir você para melhorar continuamente nossos serviços.")

# --- FORMULÁRIO ---
nota = st.select_slider("Em uma escala de 0 a 10, o quanto você recomendaria a Labor Engenharia para outra empresa?", options=list(range(11)), value=10)

if nota >= 9:
    pergunta_feedback = "O que mais contribuiu para você dar essa nota à Labor Engenharia?"
elif nota >= 7:
    pergunta_feedback = "O que poderíamos melhorar para que sua experiência fosse excelente?"
else:
    st.warning("Sua resposta é muito importante para corrigirmos falhas reais.")
    pergunta_feedback = "O que não atendeu às suas expectativas nos serviços prestados?"

feedback = st.text_area(pergunta_feedback)

st.divider()
st.subheader("Como você avalia os pontos abaixo?")
opcoes = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]

col1, col2 = st.columns(2)
with col1:
    p1 = st.select_slider("Clareza técnica", options=opcoes, value="Excelente")
    p2 = st.select_slider("Cumprimento de prazos", options=opcoes, value="Excelente")
with col2:
    p3 = st.select_slider("Comunicação", options=opcoes, value="Excelente")
    p4 = st.select_slider("Atendimento/Suporte", options=opcoes, value="Excelente")

st.divider()
contato = st.radio("Autoriza nosso contato para tratar sobre sua resposta?", ["Sim", "Não"], index=1)

# --- BOTÃO DE ENVIO COM CONEXÃO ---
if st.button("Enviar Avaliação"):
    try:
        # Tenta estabelecer a conexão definida nos Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Prepara a linha de dados
        nova_linha = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "nota": nota,
            "feedback": feedback,
            "clareza": p1,
            "prazos": p2,
            "comunicacao": p3,
            "atendimento": p4,
            "contato": contato
        }
        
        # Lê dados atuais (ou cria novo se falhar)
        try:
            df_atual = conn.read(ttl=0)
            df_final = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
        except:
            df_final = pd.DataFrame([nova_linha])
        
        # Grava na planilha
        conn.update(data=df_final)
        
        # MENSAGEM FINAL AO CLIENTE
        st.balloons()
        st.success("Agradecemos seu tempo e sua parceria!")
        st.write("Suas respostas serão analisadas pela diretoria da Labor Engenharia para aprimorar nossos serviços.")
        
    except Exception as e:
        st.error(f"Erro de conexão com a planilha. Verifique se as 'Secrets' estão corretas e se a planilha está compartilhada como 'Editor'.")
        st.exception(e) # Isso mostrará o erro técnico para você investigar
