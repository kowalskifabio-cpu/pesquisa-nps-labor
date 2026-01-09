import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Labor Engenharia - Pesquisa", page_icon="🛡️")

# --- ESTILO VISUAL (AZUL LABOR) ---
st.markdown("""
    <style>
    .stButton>button { background-color: #004a80; color: white; width: 100%; }
    .stProgress > div > div > div > div { background-color: #004a80; }
    </style>
    """, unsafe_allow_html=True)

st.image("https://laborsmt.com.br/wp-content/uploads/2023/04/logo-labor.png", width=200) # Link da sua logo

st.title("Sua opinião é fundamental")
st.write("A Labor Engenharia quer ouvir você para melhorar continuamente.")

# --- PERGUNTA 1: NPS ---
nota = st.select_slider(
    "Em uma escala de 0 a 10, o quanto você recomendaria a Labor Engenharia para outra empresa?",
    options=list(range(11)), value=10
)

# --- LÓGICA CONDICIONAL ---
if nota >= 9:
    msg = "O que mais contribuiu para você dar essa nota à Labor Engenharia?"
elif nota >= 7:
    msg = "O que poderíamos melhorar para que sua experiência fosse excelente (nota 9 ou 10)?"
else:
    st.warning("Sua resposta é muito importante para que possamos corrigir falhas reais.")
    msg = "O que não atendeu às suas expectativas nos serviços prestados pela Labor Engenharia?"

feedback = st.text_area(msg)

# --- PERGUNTA 3: PONTOS CHAVE ---
st.subheader("Avaliação de Pontos-Chave")
opcoes = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]

col1, col2 = st.columns(2)
with col1:
    clareza = st.select_slider("Clareza das orientações", options=opcoes, value="Excelente")
    prazos = st.select_slider("Cumprimento de prazos", options=opcoes, value="Excelente")
    comunicacao = st.select_slider("Facilidade de comunicação", options=opcoes, value="Excelente")
with col2:
    atendimento = st.select_slider("Atendimento e suporte", options=opcoes, value="Excelente")
    custo = st.select_slider("Custo-benefício", options=opcoes, value="Excelente")

# --- PERGUNTA 4: CONTATO ---
contato = st.radio("Caso seja necessário, você autoriza nosso contato para tratar sobre sua resposta?", ["Sim", "Não"])

# --- BOTÃO DE ENVIO ---
if st.button("Enviar Avaliação"):
    st.success("Obrigado! Suas respostas foram enviadas diretamente à nossa diretoria.")
    # Aqui depois conectaremos a gravação automática no Google Sheets
