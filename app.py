import streamlit as st
import requests
import json
import base64
import streamlit.components.v1 as components
import re
import urllib.parse

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="YİĞİT AI", page_icon="🧠", layout="wide")

# --- API KEYS ---
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# --- SESSION STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOL YAN MENÜ (SIDEBAR & SEÇENEKLER) ---
with st.sidebar:
    st.title("YİĞİT AI SEÇENEKLER")
    st.write("---")
    
    # 1. MOD SEÇİMİ
    st.subheader("🎯 Çalışma Modu")
    ai_mode = st.selectbox(
        "Uzmanlık Alanı Seçin:",
        ["Genel Asistan", "🎨 Görsel Tasarım & Çizim Uzmanı", "🌍 Google Arama & Haritalar", "💻 Teknoloji & Yazılım", "🎵 Müzik Uzmanı"]
    )
    
    # SIKI KİMLİK TANIMI
    base_prompt = (
        "Senin adın Yiğit AI. Sen YİĞİT tarafından geliştirilmiş özel bir yapay zekasın. "
        "Asla 'Flint', 'Recursive', 'ChatGPT' veya 'OpenAI' gibi başka isimler kullanmayacaksın. "
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
        content_val = m['content']
        if isinstance(content_val, dict):
            content_text = content_val.get("text", "")
        elif isinstance(content_val, list):
            content_text = " ".join([p.get("text", "") for p in content_val if isinstance(p, dict)])
        else:
            content_text = str(content_val)
        txt_history += f"{role_name}: {content_text}\n\n"
        
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

# --- ANA EKRAN (SADECE BAŞLIK) ---
st.title("YİĞİT AI")

# --- DOSYA VE GÖRSEL YÜKLEME KÖŞESİ ---
with st.expander("📁 Dosya & Görsel Analiz Köşesi"):
    uploaded_file = st.file_uploader("Görsel veya dosya yükleyin", type=None)
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
                    "image_url": {
                        "url": f"data:{mime_type};base64,{encoded_image}"
                    }
                }
                st.image(file_bytes, caption=f"Yüklenen Görsel: {file_name}", width=300)
                st.success(f"🖼️ **'{file_name}'** yüklendi!")
            else:
                try:
                    decoded_text = file_bytes.decode("utf-8")
                    file_info = f"--- DOSYA ADI: {file_name} ---\n{decoded_text}"
                except UnicodeDecodeError:
                    file_info = f"--- DOSYA ADI: {file_name} (İkili Belge) ---"
                st.success(f"📎 **'{file_name}'** yüklendi!")
        except Exception as e:
            st.error(f"Hata: {str(e)}")

# --- MESAJLARI EKRANA YAZDIRMA VE SESLİ OKUMA ---
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    st.markdown(part["text"])
                elif part.get("type") == "image_url":
                    st.image(part["image_url"]["url"], width=300)
        elif isinstance(content, dict) and "generated_image" in content:
            st.image(content["generated_image"], caption="Yiğit AI Tarafından Üretildi", width=500)
            st.markdown(content["text"])
        else:
            st.markdown(content)
            
        if message["role"] == "assistant":
            if isinstance(content, dict):
                text_to_read = content.get("text", "Görsel yanıtı.")
            elif isinstance(content, str):
                text_to_read = content
            else:
                text_to_read = "Yanıt."
                
            clean_text = re.sub(r'[\*#_`~-]', '', text_to_read)
            clean_text = clean_text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
            
            voice_html = f"""
            <div style="margin-top: 5px;">
                <button onclick="speakText_{idx}()" style="background-color: #ff4b4b; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px;">
                    🔊 Sesli Dinle
                </button>
                <button onclick="stopSpeech()" style="background-color: #555; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px; margin-left: 5px;">
                    ⏹️ Durdur
                </button>
            </div>
            <script>
                function speakText_{idx}() {{
                    window.speechSynthesis.cancel();
                    var utterance = new SpeechSynthesisUtterance("{clean_text}");
                    utterance.lang = 'tr-TR';
                    utterance.rate = 1.0;
                    window.speechSynthesis.speak(utterance);
                }}
                function stopSpeech() {{
                    window.speechSynthesis.cancel();
                }}
            </script>
            """
            components.html(voice_html, height=50)

# --- KULLANICI GİRDİSİ VE API İSTEĞİ ---
prompt = st.chat_input("Yiğit AI'ya bir şey sorun...")

if prompt:
    if not api_key:
        st.error("OpenRouter API anahtarı bulunamadı! Lütfen Streamlit Secrets bölümüne 'OPENROUTER_API_KEY' ekleyin.")
    else:
        image_triggers = ["resmini çiz", "görselini çiz", "resim çiz", "görsel çiz", "resmini yap", "fotoğrafını çiz", "draw ", "generate image"]
        is_image_request = any(trig in prompt.lower() for trig in image_triggers) or (ai_mode == "🎨 Görsel Tasarım & Çizim Uzmanı" and len(prompt) > 3)

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

        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            api_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                m_content = m["content"]
                if isinstance(m_content, dict) and "text" in m_content:
                    api_messages.append({"role": m["role"], "content": m_content["text"]})
                elif isinstance(m_content, str):
                    api_messages.append({"role": m["role"], "content": m_content})
                elif isinstance(m_content, list):
                    api_messages.append({"role": m["role"], "content": m_content})
            
            # GÜNCEL VE DİRENÇLİ MODEL LİSTESİ
            free_models = [
                "google/gemini-2.0-flash-lite-001:free",
                "qwen/qwen-2.5-7b-instruct:free",
                "meta-llama/llama-3.3-70b-instruct:free"
            ]
            
            success = False
            response_text = ""
            last_error = ""

            for model_name in free_models:
                payload = {
                    "model": model_name,
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
                        success = True
                        break
                    else:
                        # 404 veya diğer hataları kaydet, döngünün sonraki modele geçmesini sağla
                        last_error = f"Model ({model_name}) Hata {response.status_code}: {response.text}"
                except Exception as e:
                    last_error = str(e)
                    continue

            if not success or not response_text:
                st.error(f"⚠️ OpenRouter Bağlantı Hatası: (Detay: {last_error})")
                response_text = "Şu an sunucular çok yoğun, lütfen birkaç saniye sonra tekrar deneyin."

            if is_image_request:
                clean_prompt = prompt.lower()
                for kw in ["resmini çiz", "görselini çiz", "resim çiz", "görsel çiz", "resmini yap", "bana", "bir", "lütfen"]:
                    clean_prompt = clean_prompt.replace(kw, "")
                clean_prompt = clean_prompt.strip() or prompt

                enhanced_img_prompt = f"4k resolution, high quality, detailed, photorealistic, {clean_prompt}"
                encoded_img_prompt = urllib.parse.quote(enhanced_img_prompt)
                generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}?width=1280&height=720&model=flux&nologo=true"
                
                st.image(generated_image_url, caption="Yiğit AI Tarafından Üretildi", width=500)
                st.markdown(response_text)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": {
                        "text": response_text,
                        "generated_image": generated_image_url
                    }
                })
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
