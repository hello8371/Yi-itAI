import streamlit as st
import requests
import json
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yiğit AI - Gelişmiş Bulut Portalı", page_icon="🧠", layout="wide")

# --- OPENROUTER API KEY ---
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# --- SESSION STATES (OTURUM DURUMLARI) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOL YAN MENÜ (SIDEBAR & AYARLAR) ---
with st.sidebar:
    st.title("🧠 Yiğit AI Paneli")
    st.success("⚡ Dinamik Bulut Modu Aktif")
    st.write("---")
    
    # 1. MOD SEÇİMİ (Teknoloji, Müzik, Genel)
    st.subheader("🎯 Çalışma Modu")
    ai_mode = st.selectbox(
        "Uzmanlık Alanı Seçin:",
        ["Genel Asistan", "💻 Teknoloji & Yazılım", "🎵 Müzik & Müzikal Uzman"]
    )
    
    # Modlara göre sistem talimatları
    base_prompt = "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş, 7/24 bulutta çalışan gelişmiş bir yapay zekasın. Seni kimin geliştirdiğini soran herkese HER ZAMAN 'Ben Yiğit tarafından geliştirildim' diyeceksin. HER ZAMAN sadece Türkçe konuşacaksın. "
    
    if ai_mode == "💻 Teknoloji & Yazılım":
        system_prompt = base_prompt + "Şu an Teknoloji ve Yazılım Modundasın. Donanım, yazılım, kodlama, işletim sistemleri ve teknoloji konularında derinlemesine teknik bilgi ver."
    elif ai_mode == "🎵 Müzik & Müzikal Uzman":
        system_prompt = base_prompt + "Şu an Müzik Modundasın. Şarkı sözü yazımı, beste yapıları, müzik tarzları ve enstrümanlar konusunda uzman bir müzik prodüktörü gibi yanıtlar ver."
    else:
        system_prompt = base_prompt + "Kullanıcıya her konuda yardımcı olan samimi ve zeki bir asistansın."

    st.write("---")
    
    # 2. SOHBET AYARLARI
    st.subheader("⚙️ Yanıt Ayarları")
    temperature = st.slider("Yaratıcılık / Esneklik:", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
    
    st.write("---")
    
    # 3. SOHBET GEÇMİŞİ YÖNETİMİ
    st.subheader("📜 Sohbet Yönetimi")
    if st.button("🗑️ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()
        
    # Sohbet Geçmişini İndirme
    if st.session_state.messages:
        chat_history_str = ""
        for m in st.session_state.messages:
            role_name = "Kullanıcı" if m["role"] == "user" else "Yiğit AI"
            chat_history_str += f"{role_name}: {m['content']}\n\n"
            
        st.download_button(
            label="📥 Sohbeti İndir (.txt)",
            data=chat_history_str,
            file_name="yigit_ai_sohbet_gecmisi.txt",
            mime="text/plain"
        )

# --- ANA EKRAN ---
st.title("🧠 Yiğit AI - Multi-Fonksiyonel Bulut Portalı")
st.write(f"Aktif Mod: **{ai_mode}**")

# --- 4. TÜM DOSYA FORMATLARINI DESTEKLEYEN YÜKLEME KÖŞESİ ---
with st.expander("📁 Evrensel Dosya Yükleyici (Tüm Uzantılar Desteklenir)"):
    # type=None sayesinde PDF, Word, Excel, PPT, Kod, Resim, Ses, Arşiv vb. TÜM dosya tipleri yüklenebilir.
    uploaded_file = st.file_uploader(
        "Herhangi bir dosya yükleyin (.pdf, .docx, .xlsx, .pptx, .txt, .py, .jpg, .png, .zip, .mp3 vb.)", 
        type=None
    )
    file_info = ""
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_size_kb = round(uploaded_file.size / 1024, 2)
        
        try:
            # Metin tabanlı dosyaları okumayı dene
            content_bytes = uploaded_file.read()
            try:
                decoded_text = content_bytes.decode("utf-8")
                file_info = f"--- DOSYA ADI: {file_name} (Boyut: {file_size_kb} KB) ---\n--- DOSYA İÇERİĞİ ---\n{decoded_text}"
            except UnicodeDecodeError:
                # İkili (Binary) dosyalar için metadatasını ve özetini hazırla
                file_info = f"--- DOSYA ADI: {file_name} (İkili/Medya/Arşiv Belgesi) ---\nDosya Tipi: {uploaded_file.type}\nDosya Boyutu: {file_size_kb} KB\nBu ikili bir dosyadır (Görsel/Ses/Video/Arşiv/Ofis Belgesi). Lütfen dosya hakkında sorunuzu yöneltin."
            
            st.success(f"📎 **'{file_name}'** ({file_size_kb} KB) başarıyla yüklendi! Artık dosya hakkında sorular sorabilirsiniz.")
        except Exception as e:
            st.error(f"Dosya işlenirken bir hata oluştu: {str(e)}")

# --- MESAJLARI EKRANA YAZDIRMA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KULLANICI GİRDİSİ VE API İSTEĞİ ---
prompt = st.chat_input("Yiğit AI'ya bir şey sorun veya yüklediğiniz dosyayı değerlendirmesini isteyin...")

if prompt:
    if not api_key:
        st.error("OpenRouter API anahtarı bulunamadı! Lütfen Streamlit Secrets bölümüne 'OPENROUTER_API_KEY' ekleyin.")
    else:
        # Eğer dosya yüklenmişse mesaja dosya içeriğini veya bilgisini dahil et
        full_user_message = prompt
        if file_info:
            full_user_message = f"{file_info}\n\n--- KULLANICI SORUSU ---\n{prompt}"
            file_info = "" # Tekrar tekrar eklenmemesi için sıfırla

        st.session_state.messages.append({"role": "user", "content": full_user_message})
        
        # Ekranda kullanıcının yazdığı sade mesajı göster
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Sistem talimatı ve sohbet geçmişi ekleme
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            payload = {
                "model": "openrouter/free",
                "messages": api_messages,
                "temperature": temperature
            }
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=35
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
