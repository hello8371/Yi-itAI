import streamlit as st
import os
import json
from datetime import datetime
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Yiğit Bulut Paneli", page_icon="☁️", layout="wide")

UPLOAD_DIR = "bulut_dosyalari"
CHAT_DIR = "sohbet_gecmisi"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_DIR, exist_ok=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("☁️ Yiğit Bulut Paneli & Yapay Zeka")

# Sol Menü (Sidebar) - API Key ve Dosya Yönetimi
with st.sidebar:
    st.header("⚙️ Yapay Zeka Ayarları")
    # Tek seferlik API anahtarı girişi (örneğin Groq veya OpenRouter)
    api_key = st.text_input("API Key (Groq / OpenRouter)", type="password")
    selected_model = st.text_input("Model Adı", value="llama3-8b-8192") # Örnek hızlı model

    st.markdown("---")
    st.header("📁 Bulut Depolama")
    
    uploaded_files = st.file_uploader(
        "Buluta Dosya Yükle", 
        accept_multiple_files=True,
        type=None
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"{len(uploaded_files)} dosya buluta kaydedildi!")

    st.markdown("---")
    st.header("💬 Sohbet Kontrolü")
    
    if st.button("🗑️ Mevcut Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Sohbeti Buluta Kaydet", use_container_width=True):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chat_filename = f"sohbet_{timestamp}.json"
            chat_filepath = os.path.join(CHAT_DIR, chat_filename)
            
            with open(chat_filepath, "w", encoding="utf-8") as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
            st.success(f"Sohbet `{chat_filename}` olarak kaydedildi!")
        else:
            st.warning("Kaydedilecek sohbet geçmişi bulunmuyor.")

# Sekmeler
tab_chat, tab_files, tab_saved_chats = st.tabs(["💬 Yapay Zeka / Sohbet", "📂 Yüklenen Dosyalar", "🗄️ Kayıtlı Sohbetler"])

# --- SEKME 1: GERÇEK YAPAY ZEKA SOHBET EKRANI ---
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Yapay zekaya bir şeyler yazın..."):
        if not api_key:
            st.warning("Lütfen sol menüden API anahtarınızı girin.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Düşünüyor...")

                try:
                    # Groq API Örneği (Hızlı ve Standart OpenAI Formatı)
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": selected_model,
                        "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    }
                    
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        bot_reply = res_json["choices"][0]["message"]["content"]
                    else:
                        bot_reply = f"API Hatası ({response.status_code}): {response.text}"
                    
                    message_placeholder.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    
                except Exception as e:
                    message_placeholder.markdown(f"Bağlantı hatası: {e}")

# --- SEKME 2: DOSYALAR ---
with tab_files:
    st.subheader("📁 Bulut Deponuzdaki Dosyalar")
    files = os.listdir(UPLOAD_DIR)
    if files:
        for file_name in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            file_path = os.path.join(UPLOAD_DIR, file_name)
            col1.write(f"📄 **{file_name}**")
            with open(file_path, "rb") as f:
                col2.download_button("İndir", data=f, file_name=file_name, key=f"dl_{file_name}")
            if col3.button("Sil", key=f"del_{file_name}"):
                os.remove(file_path)
                st.rerun()
    else:
        st.info("Henüz dosya yok.")

# --- SEKME 3: KAYITLI SOHBETLER ---
with tab_saved_chats:
    st.subheader("🗄️ Geçmiş Sohbetler")
    saved_chats = os.listdir(CHAT_DIR)
    if saved_chats:
        selected_chat = st.selectbox("Sohbet Seç", saved_chats)
        if st.button("Sohbeti Yükle"):
            chat_filepath = os.path.join(CHAT_DIR, selected_chat)
            with open(chat_filepath, "r", encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
            st.success("Sohbet yüklendi!")
            st.rerun()
    else:
        st.info("Kayıtlı sohbet bulunmuyor.")
