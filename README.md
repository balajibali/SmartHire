# AI Resume Screening System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![AI](https://img.shields.io/badge/AI-Ollama%20Llama3-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

An AI-powered Resume Screening System developed using **Python**, **Streamlit**, **SQLite**, and **Ollama (Llama 3)**. The application helps HR professionals automate resume screening by extracting candidate information, matching resumes with job requirements, ranking candidates based on skills, and providing AI-assisted insights.

---

# Features

- 🔐 Secure HR Login and Authentication
- 📋 Job Posting Management
- 📄 Resume Upload and Parsing
- 🤖 AI-Powered Resume Screening
- 🎯 Skill Extraction and Matching
- 📊 Candidate Ranking
- 👥 Candidate Management
- 💬 AI Chat Assistant
- 📈 Recruitment Analytics Dashboard
- 🔍 Search and Filter Candidates
- 🗄 SQLite Database Integration

---

# Technology Stack

## Frontend
- Streamlit
- HTML
- CSS

## Backend
- Python

## Database
- SQLite

## AI Model
- Ollama
- Llama 3

---

# Libraries Used

- streamlit
- pandas
- plotly
- requests
- python-dotenv
- PyPDF2
- pdfplumber
- python-docx
- Pillow

---

# Project Structure

```text
AI-Resume-Screening/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── assets/
├── auth/
├── database/
├── pages/
├── scripts/
├── services/
└── utils/
```

---

# Installation

## Clone the Repository

```bash
git clone https://github.com/balajibali/balaji.git
cd balaji
```

## Create Virtual Environment (Optional)

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create a file named `.env`.

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
OLLAMA_URL=http://127.0.0.1:11434/api/generate
MODEL=llama3
```

---

# Install Ollama

Download Ollama:

https://ollama.com

Pull the model:

```bash
ollama pull llama3
```

Start Ollama:

```bash
ollama serve
```

---

# Run the Application

```bash
streamlit run app.py
```

Open your browser:

```
http://localhost:8501
```

---



# System Workflow

1. HR logs into the system.
2. HR creates job postings.
3. Candidates upload resumes.
4. Resume content is extracted.
5. Skills are identified automatically.
6. AI compares resumes with job requirements.
7. Match scores are calculated.
8. Candidates are ranked.
9. HR reviews analytics and AI insights.

---

# Future Enhancements

- Multi-language Resume Support
- OCR Support for Scanned Resumes
- Interview Scheduling
- Email Notifications
- AI Interview Question Generator
- Resume Recommendation Engine
- Cloud Database Integration
- Role-Based Access Control
- PDF Report Generation
- Cloud Deployment

---

# Requirements

- Python 3.10 or later
- Streamlit
- SQLite
- Ollama
- Llama 3

---

# Author

**B. Balaji**

Master of Computer Applications (MCA)

AI Resume Screening System

---

# Acknowledgements

- Python
- Streamlit
- SQLite
- Plotly
- Ollama
- Llama 3
- Open Source Community

---

