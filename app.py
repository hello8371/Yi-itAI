import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import base64
import streamlit.components.v1 as components
import re

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yiğit AI Premium - Yerel Bulut", page_icon="💎", layout="wide")

# --- MODELİ YÜKLEME (Önbelleğe Alınır) ---
@st.cache_resource
def load_ai_model():
    # Hugging Face üzerinde doğrudan çalışan güçlü ve hızlı yerel model
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return pipe

with st.spinner("Yiğit AI bulut sunucusunda yükleniyor, lütfen bekleyin..."):
    ai_pipeline = load_ai_model()

# --- SESSION STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOL YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("💎 Yiğit AI Premium")
    st.markdown("**Özel Yerel Bulut Sürümü**")
    st.write("Bu sistem tamamen Yiğit'in bulut sunucusunda, harici API'siz çalışır.")
    st.write("---")
    
    ai_mode = st.selectbox(
        "Çalışma Modu",
        ["Genel Sohbet", "💻 Teknoloji & Yazılım", "🎨 Yaratıcı Yazar"],
        label_visibility="collapsed"
    )
    
    base_prompt = (
        "Senin adın Yiğit AI. YİĞİT tarafından geliştirilmiş özel bir yapay zekasın. "
        "Asla ChatGPT veya başka bir servis olduğunu söyleme. "
        "Türkçe konuşulduğunda daima akıcı Türkçe ile yanıt ver."
    )
    
    if st.button("🗑️ Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# --- ANA EKRAN ---
st.title("💎 Yiğit AI - YEREL BULUT SÜRÜMÜ")
st.write(f"Aktif Mod: **{ai_mode}** | Doğrudan Bulut Gücü Aktif")
st.write("---")

# --- GEÇMİŞİ EKRANA YAZDIRMA ---
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant":
            clean_text = re.sub(r'[\*#_`~-]', '', message["content"])
            clean_text = clean_text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
            
            voice_html = f"""
            <div style="margin-top: 5px;">
                <button onclick="speakText_{idx}()" style="background-color: #ff4b4b; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px;">
                    🔊 Sesli Dinle
                </button>
            </div>
            <script>
                function speakText_{idx}() {{
                    window.speechSynthesis.cancel();
                    var utterance = new SpeechSynthesisUtterance("{clean_text}");
                    utterance.lang = 'tr-TR';
                    window.speechSynthesis.speak(utterance);
                }}
            </script>
            """
            components.html(voice_html, height=50)

# --- KULLANICI GİRDİSİ VE YEREL ÇALIŞTIRMA ---
prompt = st.chat_input("Bulut yapay zekanıza bir şeyler yazın...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Yiğit AI bulutta düşünüyor..."):
            try:
                # Konuşma geçmişini formüle et
                formatted_messages = [{"role": "system", "content": base_prompt}]
                for m in st.session_state.messages:
                    formatted_messages.append({"role": m["role"], "content": m["content"]})
                
                # Yerel modelden yanıt üret
                outputs = ai_pipeline(
                    formatted_messages,
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                
                # Üretilen yanıtı al
                response_text = outputs[0]["generated_text"][-1]["content"]
            except Exception as e:
                response_text = f"Yerel model çalıştırılırken bir hata oluştu: {str(e)}"
                
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
