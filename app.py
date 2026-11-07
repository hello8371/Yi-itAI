import requests
import streamlit as st

st.set_page_config(page_title="YiğitAI", page_icon="💎", layout="wide")

st.title("💎 YiğitAI Komuta Merkezi")
st.write("---")

# Sohbet geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girdisi
if prompt := st.chat_input("YiğitAI'ya bir şey sorun..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("YiğitAI düşünüyor..."):
            try:
                # En hafif ve en hızlı yanıt mekanizması (Pollinations / Hafif API)
                response = requests.post(
                    "https://text.pollinations.ai/",
                    json={
                        "messages": [{"role": "user", "content": prompt}],
                        "model": "openai",
                        "seed": 42
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    answer = response.text
                else:
                    answer = "Sunucu yoğun, ancak hızlıca işleme alıyorum. Tekrar dener misin?"
            except Exception as e:
                answer = f"Bağlantı hatası: {str(e)}"
                
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
