import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre no topo) ---
st.set_page_config(page_title="Sejump | Opus Mage AI", page_icon="🔱", layout="wide")

# --- 2. BANCO DE DADOS & MEMÓRIA ---
DB_FILE = "database_opus_v26.json"

def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"historico": [], "preferencias": {}, "conhecimento": []}
    return {"historico": [], "preferencias": {}, "conhecimento": []}

def salvar_dados(dados):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

memoria = carregar_dados()

# --- 3. LÓGICA DE LOGIN (SESSÃO) ---
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 4. ESTILO VISUAL SEJUMP ---
st.markdown("""
    <style>
    .stApp, header, section[data-testid="stSidebar"], .stSidebar > div { background-color: #000000 !important; }
    html, body, p, span, label, .stMarkdown { color: #f0f0f0 !important; font-family: 'Inter', sans-serif; }
    .stChatMessage { background-color: #0d0d0d !important; border: 1px solid #222 !important; border-radius: 12px !important; margin-bottom: 10px; }
    
    /* Estilo do botão de login */
    .stButton>button { 
        background-color: #111 !important; 
        border: 1px solid #333 !important; 
        color: white !important; 
        width: 100%;
        border-radius: 10px;
        height: 3em;
    }
    .stButton>button:hover { border-color: #7d33ff !important; color: #7d33ff !important; }
    
    .login-box {
        text-align: center;
        padding: 50px;
        border: 1px solid #222;
        border-radius: 20px;
        background-color: #050505;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. TELA DE LOGIN ---
if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class='login-box'>
                <h1 style='color: #7d33ff;'>🔱 SEJUMP</h1>
                <p style='color: #888;'>Acesse o Nexus do Opus Mage</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("Fazer Login com Google"):
            # Simulação de login - Futuramente conectaremos a API real
            st.session_state.logado = True
            st.rerun()
        st.caption("Aviso: Ambiente seguro e criptografado.")

# --- 6. ÁREA DO OPUS MAGE (LOGADA) ---
else:
    # --- BARRA LATERAL MULTI-MÓDULOS ---
    with st.sidebar:
        st.title("🔱 Opus Nexus v2.6")
        st.write(f"Conectado como: **Mestre da Sejump**")
        
        aba1, aba2, aba3 = st.tabs(["⚙️ Modos", "📚 Memória", "🛠️ Ferramentas"])
        
        with aba1:
            st.subheader("Modos de IA")
            m_code = st.toggle("💻 Modo Code", value=True)
            m_analise = st.toggle("📊 Modo Análise")
            m_entrevista = st.toggle("🎙️ Modo Entrevista")
            m_jogo = st.toggle("🎮 Modo Jogo")
            m_simula = st.toggle("🧪 Modo Simulação")
            m_cria = st.toggle("🎨 Modo Criação")

        with aba2:
            st.subheader("Banco de Conhecimento")
            if st.button("🗑️ Limpar Histórico"):
                memoria["historico"] = []
                salvar_dados(memoria)
                st.session_state.chat_msgs = []
                st.rerun()
            st.write(f"Logs: {len(memoria['historico'])}")
            
        with aba3:
            st.subheader("Sistema")
            st.checkbox("Proteção Sejump Ativa", value=True)
            if st.button("🚪 Sair do Sistema"):
                st.session_state.logado = False
                st.rerun()

    # --- ENGINE DE TEXTO (OPUS) ---
    GROQ_KEY = "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" 

    st.title("OpusAI | Nexus Sejump")

    # Exibir Histórico
    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = memoria["historico"]

    for m in st.session_state.chat_msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # LOGICA DE RESPOSTA
    if prompt := st.chat_input("Diga algo ao Opus..."):
        st.session_state.chat_msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Construindo a Personalidade
                contexto = "Você é o Opus, a IA oficial da Sejump. "
                if m_code: contexto += "Priorize códigos limpos e técnicos. "
                if m_entrevista: contexto += "Atue como um entrevistador profissional. "
                if m_simula: contexto += "Simule cenários e resultados possíveis. "
                if m_analise: contexto += "Analise dados e identifique padrões. "
                
                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "system", "content": contexto}] + st.session_state.chat_msgs
                    }
                )
                
                txt = r.json()["choices"][0]["message"]["content"]
                st.markdown(txt)
                st.session_state.chat_msgs.append({"role": "assistant", "content": txt})
                
                # Salvar no Banco
                memoria["historico"] = st.session_state.chat_msgs
                salvar_dados(memoria)
                
            except Exception as e:
                st.error(f"Erro no Kernel: {e}")

    # POP-UP DE ATUALIZAÇÃO (Apenas na primeira vez)
    if "v26_ready" not in st.session_state:
        st.session_state.v26_ready = True

    @st.dialog("✅ Nexus v2.6 Online")
    def show_update():
        st.write("Site da Sejump configurado com sucesso!")
        st.write("- Tela de login adicionada.")
        st.write("- Layout responsivo para iPhone/Android.")
        if st.button("Explorar"):
            st.session_state.v26_ready = False
            st.rerun()

    if st.session_state.v26_ready: show_update()