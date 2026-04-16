import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sejump | Opus Mage AI", page_icon="🔱", layout="wide")

# --- 2. ESTILO VISUAL (DARK MODE SEJUMP) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
    .stChatMessage { background-color: #0d0d0d !important; border: 1px solid #222 !important; border-radius: 15px; }
    h1, h2, h3, p, span { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .stButton>button { 
        background-color: #7d33ff !important; 
        color: white !important; 
        border-radius: 10px; 
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE SESSÃO E BANCO DE DADOS ---
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def carregar_dados(user_id):
    path = f"db_{user_id}.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"historico": []}
    return {"historico": []}

def salvar_dados(user_id, dados):
    path = f"db_{user_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- 4. TELA DE LOGIN ---
if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='text-align:center; padding:40px; border:1px solid #333; border-radius:20px; background-color:#0a0a0a;'>
                <h1 style='color:#7d33ff; margin-bottom:0;'>🔱 SEJUMP</h1>
                <p style='color:#666;'>Portal de Acesso Opus Mage</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_input = st.text_input("Identifique-se (Nome ou E-mail):")
            entrar = st.form_submit_button("INICIAR PROTOCOLO")
            
            if entrar:
                if user_input:
                    # Normaliza o ID do usuário para evitar erros de arquivo
                    clean_id = user_input.lower().strip().replace(" ", "_").replace("@", "_").replace(".", "_")
                    st.session_state.user_id = clean_id
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.warning("Mestre, forneça uma identidade para o Nexus.")

# --- 5. ÁREA LOGADA (OPUS MAGE) ---
else:
    user_id = st.session_state.user_id
    memoria = carregar_dados(user_id)
    
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = memoria["historico"]

    # Barra Lateral
    with st.sidebar:
        st.title("🔱 Nexus Sejump")
        st.write(f"Usuário: `{user_id}`")
        st.divider()
        if st.button("🚪 Encerrar Sessão"):
            st.session_state.logado = False
            st.session_state.chat_msgs = []
            st.rerun()

    # Chat principal
    st.title("OpusAI | Online")
    
    # Mostrar histórico
    for msg in st.session_state.chat_msgs:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do Usuário
    if prompt := st.chat_input("Envie um comando..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Busca a chave nos Secrets
                api_key = st.secrets["GROQ_API_KEY"]
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "Você é o Opus, a IA mística da Sejump. Seja técnico e direto."}
                        ] + st.session_state.chat_msgs
                    }
                )
                
                if response.status_code == 200:
                    resposta_ia = response.json()["choices"][0]["message"]["content"]
                    st.markdown(resposta_ia)
                    st.session_state.chat_msgs.append({"role": "assistant", "content": resposta_ia})
                    # Salva no arquivo individual
                    memoria["historico"] = st.session_state.chat_msgs
                    salvar_dados(user_id, memoria)
                else:
                    st.error(f"Erro na API Groq: {response.status_code}")
            except Exception as e:
                st.error(f"Falha no Kernel: {e}")
