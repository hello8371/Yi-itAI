import streamlit as st
import base64
import streamlit.components.v1 as components
import re

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Yiğit AI Premium - Yerel Bulut", page_icon="💎", layout="wide")

# --- MODELİ GÜVENLİ VE HAFİF YÜKLEME ---
@st.cache_resource
def load_ai_model():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        
        # Çok daha az bellek tüketen ultra hafif model
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        return pipe, None
    except Exception as e:
        return None, str(e)

with st.spinner("Yiğit AI yerel bulut motoru yükleniyor, lütfen bekleyin..."):
    ai_pipeline, error_message = load_ai_model()

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

if error_message:
    st.error(f"⚠️ Model Yükleme Hatası: {error_message}")
else:
    # --- GEÇMİŞİ EKRANA YAZDIRMA VE SESLİ OKUMA ---
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

    # --- KULLANICI GİRDİSİ VE YEREL ÇALIŞTIRMA ---
    prompt = st.chat_input("Bulut yapay zekanıza bir şeyler yazın...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Yiğit AI bulutta düşünüyor..."):
                try:
                    formatted_messages = [{"role": "system", "content": base_prompt}]
                    for m in st.session_state.messages:
                        formatted_messages.append({"role": m["role"], "content": m["content"]})
                    
                    outputs = ai_pipeline(
                        formatted_messages,
                        max_new_tokens=256,
                        do_sample=True,
                        temperature=0.7,
                        top_p=0.9
                    )
                    response_text = outputs[0]["generated_text"][-1]["content"]
                except Exception as e:
                    response_text = f"Yerel model çalıştırılırken bir hata oluştu: {str(e)}"
                    
            st.markdown(response_text)
            
            clean_text = re.sub(r'[\*#_`~-]', '', response_text)
            clean_text = clean_text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
            current_idx = len(st.session_state.messages)
            
            voice_html = f"""
            <div style="margin-top: 5px;">
                <button onclick="speakText_{current_idx}()" style="background-color: #ff4b4b; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px;">
                    🔊 Sesli Dinle
                </button>
                <button onclick="stopSpeech()" style="background-color: #555; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer; font-size: 13px; margin-left: 5px;">
                    ⏹️ Durdur
                </button>
            </div>
            <script>
                function speakText_{current_idx}() {{
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
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
