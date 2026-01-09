import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Labor Engenharia - Pesquisa NPS", page_icon="🛡️")

# --- ESTILO VISUAL PERSONALIZADO (CORES DA LABOR) ---
# Cor Laranja: #f37021 | Cor Branca: #ffffff
st.markdown(f"""
    <style>
    /* Cor do botão */
    .stButton>button {{
        background-color: #f37021;
        color: white;
        border-radius: 5px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #d65d1a;
        color: white;
    }}
    /* Cor do Slider (Escala) */
    div[data-baseweb="slider"] > div > div {{
        background-color: #f37021;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO COM LOGO ---
# Usando a logo oficial do seu site
st.image("https://laborsmt.com.br/wp-content/uploads/2023/04/logo-labor.png", width=250)

st.title("Pesquisa de Satisfação")
st.write("A **Labor Engenharia** está a realizar uma pesquisa rápida para avaliar a experiência dos nossos clientes.")

# --- PERGUNTA 1: NPS ---
st.subheader("O quanto recomendaria a Labor Engenharia?")
nota = st.select_slider(
    "Numa escala de 0 a 10, qual a probabilidade de nos recomendar a outra empresa?",
    options=list(range(11)), value=10
)

# --- LÓGICA CONDICIONAL DE FEEDBACK ---
if nota >= 9:
    texto_pergunta = "O que mais contribuiu para nos dar esta nota?"
elif nota >= 7:
    texto_pergunta = "O que poderíamos melhorar para que a sua experiência fosse excelente (nota 9 ou 10)?"
else:
    st.warning("A sua resposta é muito importante para podermos corrigir falhas reais.")
    texto_pergunta = "O que não atendeu às suas expectativas nos serviços prestados?"

feedback = st.text_area(texto_pergunta)

# --- PERGUNTA 3: PONTOS-CHAVE ---
st.divider()
st.subheader("Como avalia os pontos abaixo?")
opcoes_matriz = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]

col1, col2 = st.columns(2)
with col1:
    p1 = st.select_slider("Clareza das orientações técnicas", options=opcoes_matriz, value="Excelente")
    p2 = st.select_slider("Cumprimento de prazos", options=opcoes_matriz, value="Excelente")
    p3 = st.select_slider("Facilidade de comunicação", options=opcoes_matriz, value="Excelente")
with col2:
    p4 = st.select_slider("Atendimento e suporte", options=opcoes_matriz, value="Excelente")
    p5 = st.select_slider("Custo-benefício dos serviços", options=opcoes_matriz, value="Excelente")

# --- PERGUNTA 4: CONTATO ---
st.divider()
contato = st.radio("Autoriza o nosso contato para dar continuidade a melhorias?", ["Sim", "Não"], index=1)

# --- BOTÃO DE ENVIO ---
if st.button("Enviar Avaliação"):
    st.balloons()
    st.success("Agradecemos o seu tempo e a sua parceria! As suas respostas serão analisadas pela nossa gestão.")
