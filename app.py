import streamlit as st
import google.generativeai as genai
from PIL import Image

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

# Sol Panel (Dosya Yükleme ve Ayarlar)
with st.sidebar:
    st.title("🧠 Yiğit AI - Bulut")
    st.success("☁️ 7/24 Bulut Modu Aktif")
    st.write("---")
    
    st.subheader("📁 Dosya & Görsel Yükleme")
    uploaded_file = st.file_uploader("Dosya veya görsel seçin...", type=["png", "jpg", "jpeg", "pdf", "txt", "csv"])
    if uploaded_file is not None:
        st.info(f"Yüklenen: {uploaded_file.name}")

    st.write("---")
    st.subheader("⚙️ Sohbet Seçenekleri")
    temperature = st.slider("Yaratıcılık", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
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
        if "file_name" in message and message["file_name"]:
            st.caption(f"📎 Ekli dosya: {message['file_name']}")

prompt = st.chat_input("Yiğit AI'ya bir şey sorun...")

if prompt or uploaded_file:
    if not api_key:
        st.error("API anahtarı bulunamadı! Lütfen Streamlit Cloud 'Secrets' bölümüne GEMINI_API_KEY eklediğinizden emin olun.")
    else:
        user_message = prompt if prompt else "Bu dosyayı analiz et."
        file_info = uploaded_file.name if uploaded_file else None
        
        # Kullanıcı mesajını geçmişe ekle
        st.session_state.messages.append({"role": "user", "content": user_message, "file_name": file_info})
        with st.chat_message("user"):
            st.markdown(user_message)
            if uploaded_file:
                st.caption(f"📎 Ekli dosya: {uploaded_file.name}")
            
        with st.chat_message("assistant"):
            try:
                genai.configure(api_key=api_key)
                
                # Model yapılandırması
                generation_config = {"temperature": temperature}
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=PREMIUM_PROMPT,
                    generation_config=generation_config
                )
                
                # İçerik hazırlığı
                content_inputs = [user_message]
                if uploaded_file:
                    if uploaded_file.type.startswith("image/"):
                        img = Image.open(uploaded_file)
                        content_inputs.append(img)
                    else:
                        file_bytes = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                        content_inputs.append(f"\n[Dosya İçeriği ({uploaded_file.name})]:\n{file_bytes}")

                # Güvenli yanıt üretme
                response = model.generate_content(content_inputs)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
 
