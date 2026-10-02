# 📚 Snap & Study

Snap & Study is an AI-powered study assistant built with Streamlit and Google Gemini.

Users can upload a photo of a question, diagram, textbook page, or handwritten notes, and Gemini explains the content in simple language. Users can also ask follow-up questions and send a summary of their study conversation to their email.

## ✨ Features

- 📸 Upload study questions, diagrams, and notes
- 🤖 AI-powered explanations using Google Gemini
- 💬 Ask follow-up questions in the same conversation
- 🧠 Get simple, student-friendly explanations
- 📧 Send the complete study summary to email
- 🔐 API keys and email credentials are stored securely using Streamlit secrets

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini
- Gmail SMTP

## 📁 Project Structure

```text
snap-and-study/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    └── secrets.toml.example