import streamlit as st

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
    }
    div[data-baseweb="slider"] > div > div {
        background-color: #f37021;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INCLUSÃO DA LOGO ---
# Esta é a URL da logo que peguei direto do seu site
st.image("https://laborsmt.com.br/wp-content/uploads/2023/04/logo-labor.png", width=250)

st.title("Sua opinião é fundamental")
st.write("A **Labor Engenharia** quer ouvir você para melhorar continuamente nossos serviços.")

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

# --- PERGUNTA 3: PONTOS-CHAVE ---
st.divider()
st.subheader("Como você avalia os pontos abaixo?")
opcoes = ["Péssimo", "Ruim", "Regular", "Bom", "Excelente"]

col1, col2 = st.columns(2)
with col1:
    st.select_slider("Clareza das orientações técnicas", options=opcoes, value="Excelente")
    st.select_slider("Cumprimento de prazos", options=opcoes, value="Excelente")
    st.select_slider("Facilidade de comunicação", options=opcoes, value="Excelente")
with col2:
    st.select_slider("Atendimento e suporte", options=opcoes, value="Excelente")
    st.select_slider("Custo-benefício dos serviços", options=opcoes, value="Excelente")

# --- CONTATO ---
st.divider()
contato = st.radio("Caso seja necessário, você autoriza nosso contato para dar continuidade a melhorias?", ["Sim", "Não"], index=1)

# --- BOTÃO DE ENVIO ---
if st.button("Enviar Avaliação"):
    st.balloons()
    st.success("Obrigado pela parceria! Suas respostas foram enviadas à diretoria.")
