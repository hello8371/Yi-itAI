import streamlit as st
from gradio_client import Client

st.set_page_config(page_title="Yiğit AI Premium - Özel Bulut", page_icon="💎", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("💎 Yiğit AI Premium")
    st.markdown("**Özel Sürüm (Kendi Bulut Sunucum)**")
    if st.button("🗑️ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

st.title("💎 Yiğit AI - ÖZEL BULUT SÜRÜMÜ")
st.write("Bağlı Bulut Sunucu: `beued/yigit-ai-backend`")
st.write("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Bulut sunucunuza bir şeyler yazın...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Kendi bulut sunucunuzdan yanıt alınıyor..."):
            try:
                client = Client("beued/yigit-ai-backend")
                result = client.predict(
                    message=prompt,
                    api_name="/predict"
                )
                response_text = str(result)
            except Exception as e:
                response_text = f"Bağlantı Hatası: {str(e)}"

        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
