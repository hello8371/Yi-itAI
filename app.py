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

# API Anahtarlarını Otomatik Algıla (5'li Kalkan)
api_keys = []
try:
    for key_name, key_value in st.secrets.items():
        if key_name.startswith("GEMINI_API_KEY"):
            api_keys.append(key_value)
except Exception:
    pass

# Sol Panel
with st.sidebar:
    st.title("🧠 Yiğit AI - Bulut")
    st.success("☁️ 7/24 Bulut Modu Aktif (Tam Kalkan)")
    st.write("---")
    st.write(f"Aktif Anahtar Sayısı: {len(api_keys)}")
    
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
    if not api_keys:
        st.error("API anahtarı bulunamadı! Lütfen Streamlit Secrets bölümünü kontrol edin.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response_text = None
            success = False
            last_error = ""
            
            # Anahtarları sırayla dener
            for idx, key in enumerate(api_keys):
                try:
                    genai.configure(api_key=key)
                    
                    # Hatada belirtilen en güncel model
                    model = genai.GenerativeModel(
                        model_name="models/gemini-3.8-flash",
                        system_instruction=PREMIUM_PROMPT
                    )
                    
                    chat_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt)
                    
                    response_text = response.text
                    success = True
                    break 
                except Exception as e:
                    last_error = str(e)
                    continue
            
            if success and response_text:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            else:
                st.error(f"Hata: {last_error}")
