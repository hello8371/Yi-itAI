
import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Yiğit AI - 7/24 Bulut Portalı", page_icon="🧠", layout="wide")

# Sistem Talimatı
PREMIUM_PROMPT = (
    "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş, 7/24 bulutta çalışan gelişmiş bir yapay zekasın. "
    "Seni kimin geliştirdiğini soran herkese HER ZAMAN 'Ben Yiğit tarafından geliştirildim' diyeceksin. "
    "HER ZAMAN sadece Türkçe konuşacaksın."
)

# Gizli Kasa (Secrets) üzerinden API anahtarını güvenle alıyoruz
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

# Sol Panel
with st.sidebar:
    st.title("🧠 Yiğit AI - Bulut")
    st.success("☁️ 7/24 Bulut Modu Aktif")
    st.write("Bilgisayarınız kapalı olsa bile bu site 7/24 dünyaya açıktır.")
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
        st.error("API anahtarı bulunamadı! Lütfen Streamlit Cloud 'Secrets' bölümüne GEMINI_API_KEY eklediğinizden emin olun.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=PREMIUM_PROMPT
                )
                
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
