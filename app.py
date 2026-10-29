import streamlit as st
import requests
import base64
import streamlit.components.v1 as components
import re
import urllib.parse
import uuid

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yiğit AI PREMİUM", page_icon="💎", layout="wide")

# --- ÇOKLU SOHBET (CHAT SESSIONS) YÖNETİMİ ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "current_session_id" not in st.session_state or st.session_state.current_session_id not in st.session_state.sessions:
    default_id = str(uuid.uuid4())
    st.session_state.sessions[default_id] = {"title": "Yeni Yerel Sohbet", "messages": []}
    st.session_state.current_session_id = default_id

# --- SOL YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("💎 Yiğit AI Yerel")
    st.write("---")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_session_id = new_id
        st.rerun()

    st.markdown("### 📜 Sohbet Geçmişi")
    for s_id in list(st.session_state.sessions.keys()):
        s_title = st.session_state.sessions[s_id]["title"]
        is_current = (s_id == st.session_state.current_session_id)
        
        col_btn, col_del = st.columns([0.8, 0.2])
        with col_btn:
            btn_label = f"💬 {s_title[:16]}..." if len(s_title) > 16 else f"💬 {s_title}"
            if is_current:
                btn_label = f"▶ {btn_label}"
            
            if st.button(btn_label, key=f"select_{s_id}", use_container_width=True):
                st.session_state.current_session_id = s_id
                st.rerun()
                
        with col_del:
            if len(st.session_state.sessions) > 1:
                if st.button("🗑️", key=f"del_{s_id}"):
                    del st.session_state.sessions[s_id]
                    if is_current:
                        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                    st.rerun()

    st.write("---")
    
    st.subheader("🎯 Çalışma Modu")
    ai_mode = st.selectbox(
        "Çalışma Modu",
        ["Genel Sohbet", "🎨 Görsel Tasarım & Çizim Uzmanı", "💻 Teknoloji & Yazılım", "🌍 Bilgi Bankası"],
        label_visibility="collapsed"
    )
    
    base_prompt = (
        "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş özel bir yapay zekasın. "
        "Asla 'ChatGPT' veya 'OpenAI' gibi ifadeler kullanma. "
        "Seni kimin geliştirdiği sorulduğunda SADECE 'Ben Yiğit tarafından geliştirildim' de. "
        "Türkçe konuşulduğunda akıcı ve net Türkçe cevap ver."
    )
    
    if ai_mode == "🎨 Görsel Tasarım & Çizim Uzmanı":
        system_prompt = base_prompt + " Şu an Görsel Tasarım Modundasın."
    elif ai_mode == "💻 Teknoloji & Yazılım":
        system_prompt = base_prompt + " Şu an Teknoloji ve Yazılım Modundasın. İleri düzey kodlama desteği sun."
    else:
        system_prompt = base_prompt + " Kullanıcıya her konuda yardımcı olan yerel bir asistansın."

    st.write("---")
    st.subheader("📁 Dosya / Veri Yükleme")
    uploaded_file = st.file_uploader("Yükle", type=None, label_visibility="collapsed")
    
    file_info = ""
    image_payload_data = None
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1].lower()
        try:
            file_bytes = uploaded_file.read()
            if file_extension in ["jpg", "jpeg", "png", "webp"]:
                encoded_image = base64.b64encode(file_bytes).decode('utf-8')
                mime_type = uploaded_file.type if uploaded_file.type else f"image/{file_extension}"
                image_payload_data = {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}
                }
                st.success(f"🖼️ **'{file_name}'** yüklendi!")
            else:
                decoded_text = file_bytes.decode("utf-8")
                file_info = f"--- DOSYA ADI: {file_name} ---\n{decoded_text}"
                st.success(f"📎 **'{file_name}'** yüklendi!")
        except Exception as e:
            st.error(f"Hata: {str(e)}")

# --- AKTİF SOHBETİ ÇEK ---
current_messages = st.session_state.sessions[st.session_state.current_session_id]["messages"]

# --- ANA EKRAN ---
st.title("💎 Yiğit AI PREMİUM")
st.write(f"Aktif Mod: **{ai_mode}")
st.write("---")

# --- MESAJLARI GÖSTER ---
for idx, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, dict) and "generated_image" in content:
            st.image(content["generated_image"], caption="Yiğit AI Tarafından Üretildi", width=500)
            st.markdown(content["text"])
        elif isinstance(content, str):
            st.markdown(content)
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    st.markdown(part["text"])
                elif part.get("type") == "image_url":
                    st.image(part["image_url"]["url"], width=300)
            
        if message["role"] == "assistant":
            text_to_read = content.get("text", "Yanıt.") if isinstance(content, dict) else (content if isinstance(content, str) else "Yanıt.")
            clean_text = re.sub(r'[\*#_`~-]', '', text_to_read).replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
            
            voice_html = f"""
            <div style="margin-top: 5px;">
                <button onclick="speakText_{idx}()" style="background-color: #ff4b4b; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px;">🔊 Sesli Dinle</button>
                <button onclick="stopSpeech()" style="background-color: #555; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px; margin-left: 5px;">⏹️ Durdur</button>
            </div>
            <script>
                function speakText_{idx}() {{
                    window.speechSynthesis.cancel();
                    var utterance = new SpeechSynthesisUtterance("{clean_text}");
                    utterance.lang = 'tr-TR';
                    window.speechSynthesis.speak(utterance);
                }}
                function stopSpeech() {{ window.speechSynthesis.cancel(); }}
            </script>
            """
            components.html(voice_html, height=50)

# --- GİRDİ ---
prompt = st.chat_input("YİĞİT AI YA BİR SORU SORUN...")

if prompt:
    if len(current_messages) == 0:
        st.session_state.sessions[st.session_state.current_session_id]["title"] = prompt[:22]

    image_triggers = ["resmini çiz", "görselini çiz", "resim çiz", "görsel çiz", "resmini yap", "draw "]
    is_image_request = any(trig in prompt.lower() for trig in image_triggers) or (ai_mode == "🎨 Görsel Tasarım & Çizim Uzmanı" and len(prompt) > 3)

    if image_payload_data:
        user_content = [{"type": "text", "text": prompt}, image_payload_data]
        current_messages.append({"role": "user", "content": user_content})
        image_payload_data = None
    else:
        full_prompt = f"{file_info}\n\n{prompt}" if file_info else prompt
        file_info = ""
        current_messages.append({"role": "user", "content": full_prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        # Ollama Formatına Uygun Mesaj Hazırlığı
        api_messages = [{"role": "system", "content": system_prompt}]
        for m in current_messages:
            m_content = m["content"]
            if isinstance(m_content, dict) and "text" in m_content:
                api_messages.append({"role": m["role"], "content": m_content["text"]})
            elif isinstance(m_content, str):
                api_messages.append({"role": m["role"], "content": m_content})
            elif isinstance(m_content, list):
                # Liste içindeki text parçalarını al
                text_part = "".join([p.get("text", "") for p in m_content if p.get("type") == "text"])
                api_messages.append({"role": m["role"], "content": text_part})
        
        # KENDİ BİLGİSAYARINDAKİ OLLAMA SUNUCUSUNA BAĞLANTI (YEREL)
        endpoint = "http://localhost:11434/v1/chat/completions"
        payload = {
            "model": "qwen2.5:7b",  # Bilgisayarındaki en güçlü model!
            "messages": api_messages,
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response_text = ""
        with st.spinner("Yiğit AI (Yerel Güç) düşünüyor..."):
            try:
                response = requests.post(endpoint, json=payload, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    response_text = result["choices"][0]["message"]["content"]
                else:
                    response_text = f"Yerel sunucu hata kodu döndürdü: {response.status_code}"
            except Exception as e:
                response_text = f"Ollama sunucusuna bağlanılamadı. Ollama'nın açık olduğundan emin olun. Hata: {str(e)}"

        if is_image_request:
            clean_prompt = prompt.lower()
            if "windows" in clean_prompt:
                enhanced_img_prompt = "Windows 11 operating system glowing blue logo, futuristic digital background, 4k resolution, photorealistic"
            else:
                for kw in ["resmini çiz", "görselini çiz", "resim çiz", "görsel çiz", "resmini yap", "bana", "bir", "lütfen", "çiz"]:
                    clean_prompt = clean_prompt.replace(kw, "")
                enhanced_img_prompt = f"4k resolution, high quality, detailed, photorealistic, {clean_prompt.strip() or prompt}"

            encoded_img_prompt = urllib.parse.quote(enhanced_img_prompt)
            generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}?width=1280&height=720&model=flux&nologo=true"
            
            st.image(generated_image_url, caption="Yiğit AI Tarafından Üretildi", width=500)
            st.markdown(response_text)
            
            current_messages.append({
                "role": "assistant", 
                "content": {
                    "text": response_text,
                    "generated_image": generated_image_url
                }
            })
        else:
            st.markdown(response_text)
            current_messages.append({"role": "assistant", "content": response_text})
        
        st.rerun()
