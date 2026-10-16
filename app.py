import streamlit as st
import requests
import json
import base64

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
    st.success("⚡ Gemini Vision & Bulut Modu Aktif")
    st.write("---")
    
    # 1. MOD SEÇİMİ
    st.subheader("🎯 Çalışma Modu")
    ai_mode = st.selectbox(
        "Uzmanlık Alanı Seçin:",
        ["Genel Asistan", "💻 Teknoloji & Yazılım", "🎵 Müzik & Müzikal Uzman"]
    )
    
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
    
    uploaded_history = st.file_uploader("📥 Eski Sohbeti Yükle (.json)", type=["json"], key="history_upload")
    if uploaded_history is not None:
        try:
            loaded_messages = json.load(uploaded_history)
            st.session_state.messages = loaded_messages
            st.success("Sohbet geçmişi yüklendi!")
            st.rerun()
        except Exception as e:
            st.error("Geçersiz dosya.")

    json_history = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button(
        label="💾 Sohbeti Kaydet/İndir (.json)",
        data=json_history,
        file_name="yigit_ai_sohbet_yedeği.json",
        mime="application/json"
    )
    
    txt_history = ""
    for m in st.session_state.messages:
        role_name = "Kullanıcı" if m["role"] == "user" else "Yiğit AI"
        txt_history += f"{role_name}: {m['content']}\n\n"
        
    st.download_button(
        label="📄 Metin Olarak İndir (.txt)",
        data=txt_history if txt_history else "Henüz mesaj yok.",
        file_name="yigit_ai_sohbet_gecmisi.txt",
        mime="text/plain"
    )
    
    st.write("---")
    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# --- ANA EKRAN ---
st.title("🧠 Yiğit AI - Multi-Fonksiyonel Bulut Portalı")
st.write(f"Aktif Mod: **{ai_mode}** | Toplam Mesaj Sayısı: **{len(st.session_state.messages)}**")

# --- 4. EVRENSEL DOSYA VE GÖRSEL YÜKLEME KÖŞESİ ---
with st.expander("📁 Dosya & Görsel Analiz Köşesi (Görseller Desteklenir)"):
    uploaded_file = st.file_uploader(
        "Görsel (.jpg, .png) veya herhangi bir dosya yükleyin", 
        type=None
    )
    file_info = ""
    image_payload_data = None
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_size_kb = round(uploaded_file.size / 1024, 2)
        file_extension = file_name.split('.')[-1].lower()
        
        try:
            file_bytes = uploaded_file.read()
            
            if file_extension in ["jpg", "jpeg", "png", "webp"]:
                encoded_image = base64.b64encode(file_bytes).decode('utf-8')
                mime_type = uploaded_file.type if uploaded_file.type else f"image/{file_extension}"
                image_payload_data = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_image}"
                    }
                }
                st.image(file_bytes, caption=f"Yüklenen Görsel: {file_name}", width=300)
                st.success(f"🖼️ **'{file_name}'** görseli başarıyla yüklendi!")
            else:
                try:
                    decoded_text = file_bytes.decode("utf-8")
                    file_info = f"--- DOSYA ADI: {file_name} ---\n{decoded_text}"
                except UnicodeDecodeError:
                    file_info = f"--- DOSYA ADI: {file_name} (İkili Belge) ---"
                st.success(f"📎 **'{file_name}'** yüklendi!")
        except Exception as e:
            st.error(f"Hata: {str(e)}")

# --- MESAJLARI EKRANA YAZDIRMA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], list):
            for part in message["content"]:
                if part.get("type") == "text":
                    st.markdown(part["text"])
                elif part.get("type") == "image_url":
                    st.image(part["image_url"]["url"], width=300)
        else:
            st.markdown(message["content"])

# --- KULLANICI GİRDİSİ VE API İSTEĞİ ---
prompt = st.chat_input("Yiğit AI'ya bir şey sorun...")

if prompt:
    if not api_key:
        st.error("OpenRouter API anahtarı bulunamadı! Lütfen Streamlit Secrets bölümüne 'OPENROUTER_API_KEY' ekleyin.")
    else:
        if image_payload_data:
            user_content_structure = [
                {"type": "text", "text": prompt},
                image_payload_data
            ]
            st.session_state.messages.append({"role": "user", "content": user_content_structure})
            image_payload_data = None
        else:
            if file_info:
                full_prompt = f"{file_info}\n\n--- KULLANICI SORUSU ---\n{prompt}"
                file_info = ""
            else:
                full_prompt = prompt
            st.session_state.messages.append({"role": "user", "content": full_prompt})
            user_content_structure = full_prompt

        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            payload = {
                "model": "google/gemini-flash-1.5:free",  # Kararlı ve ücretsiz Gemini Vision modeli
                "messages": api_messages,
                "temperature": temperature
            }
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=45
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
