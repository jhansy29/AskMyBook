# 📚 Conversational Book Reader using Gemini AI

This web app enables users to upload a **PDF book** and **ask questions via voice**, receiving real-time **AI-generated answers** as both text and audio. It leverages **Google Gemini API** for multimodal reasoning and **gTTS** for speech synthesis.



---

## ✨ Features

- 📤 Upload PDF books to use as a knowledge base
- 🎙️ Record audio questions from the browser
- 🤖 Use Google Gemini API for contextual answers (PDF + audio)
- 🔊 Convert answers to speech using `gTTS`
- 📁 Download text/audio responses
- ☁️ Deployed on Google Cloud Run (Dockerized)

---

## 🛠️ Tech Stack

- **Frontend**: HTML + JavaScript (MediaRecorder API)
- **Backend**: Python (Flask)
- **AI Models**: Google Gemini API
- **Speech Synthesis**: gTTS (Google Text-to-Speech)
- **Deployment**: Docker + Google Cloud Run

---

## 📦 Installation

```bash
git clone https://github.com/jhansy29/convai_finalproject.git
cd convai_finalproject
pip install -r requirements.txt
python main.py
