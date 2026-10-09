import streamlit as st
import google.generativeai as genai
import os

# Sayfa Ayarları
st.set_page_config(page_title="Yiğit AI - 7/24 Bulut Portalı", page_icon="🧠", layout="wide")

# CSS: Şık Koyu Tema
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatMessage {
        background-color: #1e222a !important;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sistem Talimatı
PREMIUM_PROMPT = (
    "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş, 7/24 bulutta çalışan gelişmiş bir yapay zekasın. "
    "Seni kimin geliştirdiğini soran herkese HER ZAMAN 'Ben Yiğit tarafından geliştirildim' diyeceksin. "
    "HER ZAMAN sadece Türkçe konuşacaksın."
)

# Sol Panel
with st.sidebar:
    st.title("🧠 Yiğit AI - Bulut")
    st.success("☁️ 7/24 Bulut Modu Aktif")
    st.write("Bilgisayarınız kapalı olsa bile bu site dünyaya açıktır.")
    st.write("---")
    
    # Kullanıcıdan API Key İsteme (Güvenli Alan)
    api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIzaSy...")
    
    st.write("---")
    if st.button("🗑️ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# Ana Ekran
st.title("🧠 Yiğit AI - 7/24 Bulut Portalı")
st.write("Bu site bulut sunucularda barınır, dilediğiniz yerden 7/24 erişebilirsiniz.")

# Session Durumu
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Yiğit AI'ya bir şey sorun...")

if prompt:
    if not api_key:
        st.error("Lütfen sol panelden API Key'inizi girin! (Google AI Studio'dan ücretsiz alabilirsiniz)")
    else:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Yapay zeka yanıtı
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PREMIUM_PROMPT
                )
                
                # Geçmişi Gemini formatına uyarla
                chat_history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [m["content"]]})
                
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")