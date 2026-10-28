import streamlit as st
import os
import json
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Yiğit Bulut Paneli", page_icon="☁️", layout="wide")

# Yüklenen dosyaların ve sohbetlerin tutulacağı klasörler
UPLOAD_DIR = "bulut_dosyalari"
CHAT_DIR = "sohbet_gecmisi"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_DIR, exist_ok=True)

# Session State Tanımlamaları
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("☁️ Yiğit Bulut Paneli")

# Sol Menü (Sidebar) - Dosya Yükleme ve Sohbet Yönetimi
with st.sidebar:
    st.header("📁 Bulut Depolama")
    
    # 1. TÜM DOSYALARI YÜKLEME
    uploaded_files = st.file_uploader(
        "Buluta Dosya Yükle", 
        accept_multiple_files=True,
        type=None  # Tüm dosya türlerine izin verir (pdf, zip, png, iso, txt vs.)
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"{len(uploaded_files)} dosya buluta kaydedildi!")

    st.markdown("---")
    st.header("💬 Sohbet Kontrolü")
    
    # 2. SOHBETİ SİLME
    if st.button("🗑️ Mevcut Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # 3. SOHBETİ KAYDETME (Buluta JSON/TXT olarak kaydeder)
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

# Ana Ekran Düzeni (Sekmeli)
tab_chat, tab_files, tab_saved_chats = st.tabs(["💬 Yapay Zeka / Sohbet", "📂 Yüklenen Dosyalar", "🗄️ Kayıtlı Sohbetler"])

# --- SEKME 1: SOHBET EKRANI ---
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("Mesajınızı yazın..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Bulut sisteminin vereceği örnek yanıt/işlem
        bot_response = f"Bulut Sistemi Mesajınızı Aldı: '{user_input}'"
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)

# --- SEKME 2: YÜKLENEN DOSYALARI LİSTELEME VE İNDİRME ---
with tab_files:
    st.subheader("📁 Bulut Deponuzdaki Dosyalar")
    files = os.listdir(UPLOAD_DIR)
    
    if files:
        for file_name in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            col1.write(f"📄 **{file_name}** ({os.path.getsize(file_path)} bytes)")
            
            # Dosya İndirme Butonu
            with open(file_path, "rb") as f:
                col2.download_button("İndir", data=f, file_name=file_name, key=f"dl_{file_name}")
            
            # Dosya Silme Butonu
            if col3.button("Sil", key=f"del_{file_name}"):
                os.remove(file_path)
                st.rerun()
    else:
        st.info("Bulut deponuzda henüz dosya yok.")

# --- SEKME 3: KAYITLI SOHBETLERİ GÖRÜNTÜLEME VE YÜKLEME ---
with tab_saved_chats:
    st.subheader("🗄️ Bulutta Saklanan Geçmiş Sohbetler")
    saved_chats = os.listdir(CHAT_DIR)
    
    if saved_chats:
        selected_chat = st.selectbox("Açılacak Sohbeti Seçin", saved_chats)
        if st.button("Seçili Sohbeti Yükle"):
            chat_filepath = os.path.join(CHAT_DIR, selected_chat)
            with open(chat_filepath, "r", encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
            st.success("Sohbet başarıyla geri yüklendi!")
            st.rerun()
    else:
        st.info("Henüz kaydedilmiş bir sohbet dosyası yok.")
