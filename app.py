import streamlit as st
import requests
import json
import base64
import streamlit.components.v1 as components
import re
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yiğit AI Premium", page_icon="💎", layout="wide")

# --- API KEYS ---
api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")

# --- SESSION STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOL YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("💎 Yiğit AI Premium")
    st.markdown("**Özel Sürüm V3.0**")
    st.write("Bu sistem tamamen Yiğit tarafından en gelişmiş özelliklerle donatılmıştır.")
    st.write("---")
    
    # 1. ÇALIŞMA MODU
    st.subheader("🎯 Çalışma Modu")
    ai_mode = st.selectbox(
        "Çalışma Modu",
        ["Genel Sohbet", "🎨 Görsel Tasarım & Çizim Uzmanı", "🌍 Google Arama & Haritalar", "💻 Teknoloji & Yazılım", "🎵 Müzik Uzmanı"],
        label_visibility="collapsed"
    )
    
    # SIKI KİMLİK TANIMI
    base_prompt = (
        "Senin adın Yiğit AI Premium. Sen YİĞİT tarafından geliştirilmiş özel bir yapay zekasın. "
        "Asla 'ChatGPT', 'OpenAI' veya 'Hugging Face' gibi başka isimler kullanmayacaksın. "
        "Seni kimin geliştirdiği sorulduğunda SADECE 'Ben Yiğit tarafından geliştirildim' diyeceksin. "
        "Türkçe konuşulduğunda Türkçe, İngilizce konuşulduğunda İngilizce cevap ver."
    )
    
    if ai_mode == "🎨 Görsel Tasarım & Çizim Uzmanı":
        system_prompt = base_prompt + " Şu an Görsel Tasarım Modundasın. Detaylı ve yaratıcı tasvirler yap."
    elif ai_mode == "🌍 Google Arama & Haritalar":
        system_prompt = base_prompt + " Şu an Google Arama ve Haritalar Modundasın. Kesin ve net bilgiler sun."
    elif ai_mode == "💻 Teknoloji & Yazılım":
        system_prompt = base_prompt + " Şu an Teknoloji ve Yazılım Modundasın. İleri düzey kodlama ve donanım analizi yap."
    elif ai_mode == "🎵 Müzik Uzmanı":
        system_prompt = base_prompt + " Şu an Müzik Modundasın. Beste ve müzik teorisinde rehberlik et."
    else:
        system_prompt = base_prompt + " Kullanıcıya her konuda yardımcı olan son derece akıllı ve samimi bir asistansın."

    st.write("---")
    
    if st.button("🗑️ Premium Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

    st.write("---")
    
    # 2. VERİ YÜKLEME KÖŞESİ
    st.subheader("📁 10 GB Premium Veri Yükleme")
    st.write("Metin, Log, Kod veya Analiz Dosyası Seçin")
    uploaded_file = st.file_uploader("Yüklemek", type=None, label_visibility="collapsed")
    st.caption("Dosya başına 10 GB • TXT, LOG, MD, JSON")
    
    file_info = ""
    image_payload_data = None
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        
        

