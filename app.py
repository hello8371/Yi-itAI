import streamlit as st
import os
import json
from datetime import datetime
import requests

# Sayfa Ayarları (Elmas Konseptli Başlık ve İkon)
st.set_page_config(page_title="💎 Yiğit AI - Elmas Bulut Paneli", page_icon="💎", layout="wide")

UPLOAD_DIR = "bulut_dosyalari"
CHAT_DIR = "sohbet_gecmisi"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_DIR, exist_ok=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Elmas Temalı Başlık
st.title("💎 Yiğit AI — Elmas Bulut & Çoklu Model Paneli")

# --- SOL MENÜ: API, MODEL VE DOSYA YÖNETİMİ ---
with st.sidebar:
    st.header("💎 Elmas AI Ayarları")
    
    provider = st.selectbox("API Sağlayıcı", ["Groq", "OpenRouter", "Hugging Face"])
    api_key = st.text_input(f"{provider} API Key", type="password")
    
    if provider == "Groq":
        default_model = "llama3-70b-8192"
    elif provider == "OpenRouter":
        default_model = "anthropic/claude-3-haiku"
    else:
        default_model = "meta-llama/Meta-Llama-3-8B-Instruct"
        
    selected_model = st.text_input("Model ID / Adı", value=default_model)

    st.markdown("---")
    st.header("📂 Elmas Bulut Depolama")
    
    uploaded_files = st.file_uploader(
        "Tüm Dosya Türlerini Yükle", 
        accept_multiple_files=True,
        type=None
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"{len(uploaded_files)} dosya elmas buluta kaydedildi!")

    st.markdown("---")
    st.header("💬 Sohbet Kontrolü")
    
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Sohbeti Buluta Kaydet", use_container_width=True):
        if st.session_state.messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chat_filename = f"elmas_sohbet_{timestamp}.json"
            chat_filepath = os.path.join(CHAT_DIR, chat_filename)
            
            with open(chat_filepath, "w", encoding="utf-8") as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
            st.success(f"Sohbet `{chat_filename}` olarak kaydedildi!")
        else:
            st.warning("Kaydedilecek sohbet geçmişi yok.")

# --- SEKME DÜZENİ ---
tab_chat, tab_files, tab_saved_chats = st.tabs(["💎 Elmas Sohbet", "📂 Bulut Dosyaları", "🗄️ Kayıtlı Sohbetler"])

# SEKME 1: ELMAS AI SOHBET EKRANI
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="💎" if msg["role"]=="assistant" else "👤"):
            st.write(msg["content"])

    if user_input := st.chat_input("Elmas AI'ya bir şeyler yazın..."):
        if not api_key:
            st.warning(f"Lütfen sol menüden {provider} API anahtarınızı girin.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)

            with st.chat_message("assistant", avatar="💎"):
                message_placeholder = st.empty()
                message_placeholder.markdown("💎 Elmas AI düşünüyor...")

                try:
                    bot_reply = ""
                    
                    if provider == "Groq":
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        payload = {
                            "model": selected_model,
                            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        }
                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                        if res.status_code == 200:
                            bot_reply = res.json()["choices"][0]["message"]["content"]
                        else:
                            bot_reply = f"Groq Hatası ({res.status_code}): {res.text}"

                    elif provider == "OpenRouter":
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "http://localhost:8501",
                            "X-Title": "Yigit Elmas AI Cloud"
                        }
                        payload = {
                            "model": selected_model,
                            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        }
                        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
                        if res.status_code == 200:
                            bot_reply = res.json()["choices"][0]["message"]["content"]
                        else:
                            bot_reply = f"OpenRouter Hatası ({res.status_code}): {res.text}"

                    elif provider == "Hugging Face":
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        payload = {
                            "inputs": user_input,
                            "parameters": {"max_new_tokens": 512}
                        }
                        url = f"https://api-inference.huggingface.co/models/{selected_model}"
                        res = requests.post(url, json=payload, headers=headers)
                        if res.status_code == 200:
                            data = res.json()
                            if isinstance(data, list) and "generated_text" in data[0]:
                                bot_reply = data[0]["generated_text"]
                            else:
                                bot_reply = str(data)
                        else:
                            bot_reply = f"Hugging Face Hatası ({res.status_code}): {res.text}"

                    message_placeholder.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    
                except Exception as e:
                    message_placeholder.markdown(f"Bağlantı hatası oluştu: {e}")

# SEKME 2: DOSYALAR
with tab_files:
    st.subheader("📂 Elmas Bulut Deponuzdaki Dosyalar")
    files = os.listdir(UPLOAD_DIR)
    if files:
        for file_name in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            file_path = os.path.join(UPLOAD_DIR, file_name)
            col1.write(f"💎 **{file_name}** ({os.path.getsize(file_path)} bytes)")
            with open(file_path, "rb") as f:
                col2.download_button("İndir", data=f, file_name=file_name, key=f"dl_{file_name}")
            if col3.button("Sil", key=f"del_{file_name}"):
                os.remove(file_path)
                st.rerun()
    else:
        st.info("Elmas bulut deponuzda henüz dosya yok.")

# SEKME 3: KAYITLI SOHBETLER
with tab_saved_chats:
    st.subheader("🗄️ Elmas Bulutta Saklanan Geçmiş Sohbetler")
    saved_chats = os.listdir(CHAT_DIR)
    if saved_chats:
        selected_chat = st.selectbox("Yüklenecek Sohbeti Seçin", saved_chats)
        if st.button("Seçili Sohbeti Geri Yükle"):
            chat_filepath = os.path.join(CHAT_DIR, selected_chat)
            with open(chat_filepath, "r", encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
            st.success("Sohbet başarıyla yüklendi!")
            st.rerun()
    else:
        st.info("Kayıtlı sohbet dosyası bulunmuyor.")
