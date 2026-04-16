import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sejump | Opus Mage AI", page_icon="🔱", layout="wide")

# --- 2. LOGIN REAL COM GOOGLE ---
# Usando a função nativa do Streamlit para simplificar
if "google_auth" not in st.session_state:
    st.session_state.logado = False

# --- TELA DE LOGIN ATUALIZADA ---
def login_form():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align:center; padding:50px; border:1px solid #222; border-radius:20px; background-color:#050505;'> <h1 style='color:#7d33ff;'>🔱 SEJUMP</h1> <p style='color:#888;'>Nexus do Opus Mage</p></div>", unsafe_allow_html=True)
        
        # Usamos um form para garantir que o clique envie os dados
        with st.form("login_nexus"):
            user = st.text_input("Digite seu Nome/E-mail:")
            submit = st.form_submit_button("ACESSAR SISTEMA")
            
            if submit:
                if user:
                    st.session_state.user_id = user.lower().replace(" ", "_").replace("@", "_").replace(".", "_")
                    st.session_state.logado = True
                    st.rerun() # Isso aqui é o que faz a mágica de trocar a tela!
                else:
                    st.error("Mestre, identifique-se primeiro!")

# --- 3. LÓGICA DE DADOS POR USUÁRIO ---
def carregar_dados(user_id):
    path = f"db_{user_id}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"historico": []}

def salvar_dados(user_id, dados):
    path = f"db_{user_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- 4. EXECUÇÃO ---
if not st.session_state.logado:
    login_form()
else:
    user_id = st.session_state.user_id
    memoria = carregar_dados(user_id)

    with st.sidebar:
        st.title(f"🔱 Nexus: {user_id}")
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    # --- ENGINE GROQ ---
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    
    st.title("OpusAI | Online")

    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = memoria["historico"]

    for m in st.session_state.chat_msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Comande o Opus..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "system", "content": "Você é o Opus da Sejump."}] + st.session_state.chat_msgs
                }
            )
            txt = r.json()["choices"][0]["message"]["content"]
            st.markdown(txt)
            st.session_state.chat_msgs.append({"role": "assistant", "content": txt})
            memoria["historico"] = st.session_state.chat_msgs
            salvar_dados(user_id, memoria)
