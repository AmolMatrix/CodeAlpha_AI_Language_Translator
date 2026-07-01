"""
AI Language Translator
-----------------------
An NLP-based AI Language Translator that detects the user's input language
and performs real-time translation with speech output and history management.

Run with:
    streamlit run app.py
"""

import io
import os
from datetime import datetime
import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory, LangDetectException
from gtts import gTTS

# Make langdetect deterministic (same input -> same detected language every time)
DetectorFactory.seed = 0

HISTORY_FILE = "history.txt"

GTTS_SUPPORTED = {
    "en", "hi", "es", "fr", "de", "zh-CN", "zh-TW", "ja", "ko", "ar", "ru",
    "pt", "it", "ta", "te", "bn", "ur", "pa", "gu", "mr",
}

# Supported languages (display name -> language code used by the translator)

LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Russian": "ru",
    "Portuguese": "pt",
    "Italian": "it",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn",
    "Urdu": "ur",
    "Punjabi": "pa",
    "Gujarati": "gu",
    "Marathi": "mr",
}

# friendly display name (e.g. "French")
LANG_CODE_TO_NAME = {code: name for name, code in LANGUAGES.items() if code != "auto"}

# Core NLP 

def detect_language(text: str):
    """Detect the language of the given text.

    Returns a tuple of (language_code, language_name).
    If detection fails, returns (None, "Unknown").
    """
    try:
        code = detect(text)
        name = LANG_CODE_TO_NAME.get(code, code)
        return code, name
    except LangDetectException:
        return None, "Unknown"


def translate_text(text: str, source_code: str, target_code: str) -> str:
    """Translate text from source_code to target_code using Google Translator."""
    try:
        translator = GoogleTranslator(source=source_code, target=target_code)
        return translator.translate(text)
    except Exception:
        translator = GoogleTranslator(source="auto", target=target_code)
        return translator.translate(text)


def text_to_speech(text: str, lang_code: str) -> io.BytesIO | None:
    tts_lang = lang_code if lang_code in GTTS_SUPPORTED else lang_code.split("-")[0]
    try:
        tts = gTTS(text=text, lang=tts_lang)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Text-to-speech failed: {e}")
        return None

# History management (simple file-based storage using the os module)

def save_history(original: str, translated: str, source_lang: str, target_lang: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] ({source_lang} -> {target_lang}) {original} ---> {translated}\n"
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def load_history() -> list[str]:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return list(reversed(lines))  # newest first


def clear_history() -> None:
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


# Streamlit UI

st.set_page_config(page_title="AI Language Translator", page_icon="🌐", layout="centered")

st.title("🌐 AI Language Translator")
st.caption(
    "An NLP-based AI Language Translator that detects user language and "
    "performs real-time translation with speech output and history management."
)

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "target_lang_code" not in st.session_state:
    st.session_state.target_lang_code = "hi"

tab_translate, tab_history = st.tabs(["🔤 Translate", "🕘 History"])

# ---------------- Translate tab ----------------
with tab_translate:
    text_input = st.text_area(
        "Enter text to translate:",
        height=120,
        placeholder="e.g. I am learning Python",
    )

    col1, col2 = st.columns(2)
    with col1:
        source_lang_name = st.selectbox("Translate from:", list(LANGUAGES.keys()), index=0)
    with col2:
        target_options = [name for name in LANGUAGES if name != "Auto Detect"]
        default_index = target_options.index("Hindi") if "Hindi" in target_options else 0
        target_lang_name = st.selectbox("Translate to:", target_options, index=default_index)

    if st.button("Translate", type="primary"):
        if not text_input.strip():
            st.warning("Please enter some text to translate.")
        else:
            # Step 1: Language detection
            if source_lang_name == "Auto Detect":
                detected_code, detected_name = detect_language(text_input)
                if detected_code is None:
                    st.error("Could not detect the language automatically. Please select it manually.")
                    st.stop()
                source_code = detected_code
                st.info(f"Detected language: **{detected_name}** ({detected_code})")
            else:
                source_code = LANGUAGES[source_lang_name]
                detected_name = source_lang_name

            target_code = LANGUAGES[target_lang_name]

            with st.spinner("Translating..."):
                translated = translate_text(text_input, source_code, target_code)

            st.success("Translation complete!")

            st.session_state.translated_text = translated
            st.session_state.target_lang_code = target_code
            save_history(text_input, translated, detected_name, target_lang_name)


    if st.session_state.translated_text:
        st.text_area("Translated text:", value=st.session_state.translated_text, height=120)

        if st.button("🔊 Speak Translation"):
            with st.spinner("Generating audio..."):
                audio_data = text_to_speech(
                    st.session_state.translated_text, st.session_state.target_lang_code
                )
            if audio_data:
                st.audio(audio_data, format="audio/mp3")

# ---------------- History tab ----------------
with tab_history:
    st.subheader("Translation History")
    history_lines = load_history()

    if not history_lines:
        st.info("No translation history yet. Translate something to get started!")
    else:
        for line in history_lines:
            st.text(line.strip())

        if st.button("🗑️ Clear History"):
            clear_history()
            st.rerun()