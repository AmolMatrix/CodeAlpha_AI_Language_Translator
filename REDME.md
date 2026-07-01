AI Language Translator (Python + Streamlit)
An NLP-based AI Language Translator that detects the user's input language and
performs real-time translation with speech output and history management.

Features:
    1.Text input — type any sentence
    2.Language selection — pick source/target language, or use Auto Detect
    3.Language detection — powered by langdetect
    4.AI translation — powered by deep-translator (Google Translate backend)
    5.Text-to-speech — hear the translated text using gTTS (Google Text-to-Speech)
    6.Translation history — every translation is logged to history.txt

1. Setup
Create a virtual environment (recommended) and install dependencies:
    python -m venv venv

2. Run the app
    streamlit run app.py
    opens the app in your browser (usually at http://localhost:8501).

Future improvements
    1.Voice input (speech-to-text) instead of typing
    2.AI-generated sentence explanations
    3.Searchable translation history
    4.Chat-style translator interface
    5.Offline translation model support

One-line project summary
    An NLP-based AI Language Translator that detects user language and performs
    real-time translation with speech output and history management.