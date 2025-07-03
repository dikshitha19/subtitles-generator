# 🎬 subtitle-generator

A powerful and user-friendly web application that generates subtitles for uploaded video files in multiple languages using OpenAI’s Whisper model.

---

🚀 Features

🎥 Upload video files directly via the web interface  
🧠 Automatically transcribes speech using OpenAI Whisper  
🌐 Supports multiple language options for transcription  
🗂️ Generates downloadable `.srt` subtitle files  
💾 Stores output files and user data securely  
⚙️ Built with Python, Flask, MoviePy, and MongoDB  

---

📁 Folder Structure

```bash
subtitles-generator/
│
├── backend/                # Flask backend logic
├── src/                    # Subtitle generation (Whisper + Hydra config)
├── static/                 # CSS, JS, client-side files
├── templates/              # HTML templates (home, login, signup, etc.)
├── uploads/                # Uploaded videos
├── output/                 # Generated subtitles
├── .gitignore              # Ignored files
├── README.md               # This file
├── requirements.txt        # Dependencies
├── server.py               # Flask entry point
└── setup.py                # (Optional) for packaging

```
🧠 Technologies Used :

Python 3.8+

Flask

OpenAI Whisper

Hydra

MongoDB

MoviePy

HTML/CSS/JS

---------------------------------------

✨ Future Plans :

Add video preview while showing subtitles

Translate subtitles to different languages

Export in .vtt and .txt formats

Integrate OAuth authentication (Google, GitHub login)

