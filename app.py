import streamlit as st
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Yiğit AI - 7/24 Bulut Portalı", page_icon="🧠", layout="wide")

# Sistem Talimatı
PREMIUM_PROMPT = (
    "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş, 7/24 bulutta çalışan gelişmiş bir yapay zekasın. "
    "Seni kimin geliştirdiğini soran herkese HER ZAMAN 'Ben Yiğit tarafından geliştirildim' diyeceksin. "
    "HER ZAMAN sadece Türkçe konuşacaksın."
)

# OpenRouter API Anahtarı
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# Sol Panel
with st.sidebar:
    st.title("🧠 Yiğit AI - Bulut")
    st.success("⚡ Dinamik Ücretsiz Havuz Aktif")
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
        st.error("OpenRouter API anahtarı bulunamadı! Lütfen Streamlit Secrets bölümüne 'OPENROUTER_API_KEY' ekleyin.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Sistem talimatı ve sohbet geçmişi
            api_messages = [{"role": "system", "content": PREMIUM_PROMPT}]
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            # OpenRouter'ın Otomatik Ücretsiz Model Yönlendiricisi
            payload = {
                "model": "openrouter/free",
                "messages": api_messages
            }
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    st.error(f"API Hatası ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Bağlantı Hatası: {str(e)}")
