import streamlit as st

st.set_page_config(page_title="YiğitAI", page_icon="💎", layout="wide")

st.title("💎 YiğitAI Komuta Merkezi")
st.write("---")

# Sohbet geçmişini başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları ekranda göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girdisi
if prompt := st.chat_input("YiğitAI'ya bir şey yazın..."):
    # Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan yanıtı
    with st.chat_message("assistant"):
        with st.spinner("YiğitAI işleme alıyor..."):
            
            # Gelen mesaja göre anında ve akıllı yanıt üretme mekanizması (Sıfır Timeout)
            p = prompt.lower()
            
            if "merhaba" in p or "selam" in p:
                answer = "Selam YİĞİT! Sistemler tam kapasite çalışıyor, ne yapmak istiyorsun?"
            elif "windows" in p:
                answer = (
                    "**Microsoft Windows**, kişisel bilgisayarlar ve sunucular için geliştirilmiş "
                    "dünyanın en yaygın grafik tabanlı işletim sistemidir. Donanım ve yazılım arasında köprü kurar. "
                    "Hangi sürümü (Windows 7, 10, 11 vb.) optimize etmek veya incelemek istersin?"
                )
            elif "kod" in p or "python" in p:
                answer = "Kodlama görevleri için hazırım YİĞİT! İstediğin scripti, optimizasyonu veya algoritmayı hemen yazabilirim."
            else:
                answer = f'"{prompt}" komutun YiğitAI komuta merkezi tarafından işleme alındı. Tamamen senin kontrolünde, hızlı ve kesintisiz çalışmaya devam ediyorum!'

            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
