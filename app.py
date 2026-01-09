import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Labor Engenharia - Pesquisa de Satisfação", page_icon="🛡️")

# --- ESTILO VISUAL (LARANJA LABOR) ---
st.markdown("""
    <style>
    /* Cor do botão e sliders */
    .stButton>button {
        background-color: #f37021;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    div[data-baseweb="slider"] > div > div {
        background-color: #f37021;
    }
    /* Estilo do rádio */
    div[data-baseweb="radio"] > div {
        flex-direction: row;
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO E TÍTULO ---
# Certifique-se de que o arquivo 'logo.png' foi carregado no seu GitHub
try:
    st.image("logo.png", width=220)
except:
    st.info("Labor Engenharia")

st.title("Sua opinião é fundamental")
st.write("A **Labor Engenharia** está realizando uma pesquisa rápida para avaliar a experiência dos nossos clientes e identificar oportunidades reais de melhoria.")
st.caption("A pesquisa leva menos de 1 minuto. Suas respostas são analisadas diretamente pela nossa gestão.")

# --- CONEXÃO COM O BANCO DE DADOS (GOOGLE SHEETS) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PERGUNTA 1: NPS ---
st.subheader("Avaliação Geral")
nota = st.select_slider(
    "Em uma escala de 0 a 10, o quanto você recomendaria a Labor Engenharia para outra empresa?",
    options=list(range(11)), 
    value=10
)

# --- PERGUNTA 2: LÓGICA CONDICIONAL ---
if nota >= 9:
    pergunta_feedback = "O que mais contribuiu para você dar essa nota à Labor Engenharia?"
elif nota >= 7:
    pergunta_feedback = "O que poderíamos melhorar para que sua experiência com a Labor Engenharia fosse excelente (nota 9 ou 10)?"
else:
    st.warning("Sua resposta é muito importante para que possamos corrigir falhas reais.")
    pergunta_feedback = "O que não atendeu às suas expectativas nos serviços prestados pela Labor Engenharia?"

feedback = st.text_area(pergunta_feedback)

# --- PERGUNTA 3: PONTOS-CHAVE ---
st.divider()
st.subheader("Como você avalia os pontos abaixo?")
opcoes_escala = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]

col1, col2 = st.columns(2)
with col1:
    clareza = st.select_slider("Clareza das orientações técnicas", options=opcoes_escala, value="Excelente")
    prazos = st.select_slider("Cumprimento de prazos", options=opcoes_escala, value="Excelente")
    comunicacao = st.select_slider("Facilidade de comunicação", options=opcoes_escala, value="Excelente")
with col2:
    atendimento = st.select_slider("Atendimento e suporte", options=opcoes_escala, value="Excelente")
    custo = st.select_slider("Custo-benefício dos serviços", options=opcoes_escala, value="Excelente")

# --- PERGUNTA 4: CONTATO ---
st.divider()
st.write("**Contato Futuro**")
contato_autorizado = st.radio(
    "Caso seja necessário, você autoriza nosso contato para dar continuidade a melhorias relacionadas à sua resposta?",
    ["Sim", "Não"], 
    index=1
)

# --- BOTÃO DE ENVIO E GRAVAÇÃO ---
if st.button("Enviar Avaliação"):
    try:
        # 1. Preparar os dados da resposta
        dados_da_resposta = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "nota": nota,
            "feedback": feedback,
            "clareza": clareza,
            "prazos": prazos,
            "comunicacao": comunicacao,
            "atendimento": atendimento,
            "custo": custo,
            "contato": contato_autorizado
        }
        
        # 2. Ler planilha atual e adicionar nova linha
        try:
            df_atual = conn.read(ttl=0)
            df_novo = pd.concat([df_atual, pd.DataFrame([dados_da_resposta])], ignore_index=True)
        except:
            df_novo = pd.DataFrame([dados_da_resposta])
        
        # 3. Atualizar a planilha no Google Sheets
        conn.update(data=df_novo)
        
        # 4. MENSAGEM FINAL PARA O CLIENTE
        st.balloons()
        st.success("Agradecemos seu tempo e sua parceria!")
        st.write("Suas respostas serão analisadas pela diretoria da Labor Engenharia e utilizadas para aprimorar continuamente nossos serviços.")
        
    except Exception as e:
        st.error("Ocorreu um erro ao enviar. Por favor, tente novamente em instantes.")
        # O erro técnico fica oculto para o cliente, mas você pode ver no console se precisar
