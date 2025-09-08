# MISRA-C Embedded Code Chatbot

A local chatbot that generates **MISRA-C:2012 compliant embedded C code** by parsing hardware datasheets (PDF).  
Built with **Python + Streamlit**, designed to run fully offline on a laptop.  

Driver file (.c/.h) integration is **planned as the next extension**.

---

## Features
- Upload hardware datasheets (PDF).
- Query chatbot for MISRA-C compliant code snippets.
- Streamlit-based simple desktop app.
- Portable: runs locally without cloud dependency.

---

## Planned Features
- Upload vendor driver files (`.c`, `.h`).
- Merge datasheet + driver context for tailored code generation.

---

## Project Structure

misra_chatbot/
│
├── app.py # Streamlit app UI
├── chatbot_engine.py # Core logic and LLM backend
├── requirements.txt # Python dependencies
├── build.bat # Script for quick environment setup
└── .venv/ # Local virtual environment (not committed)


---

## Setup & Run
```bash
### 1. Clone repository

git clone https://github.com/<USERNAME>/misra-c-chatbot.git
cd misra-c-chatbot

2. Create virtual environment
python -m venv .venv

3. Activate environment

Windows (cmd):

.venv\Scripts\activate.bat


PowerShell:

.\.venv\Scripts\Activate.ps1

4. Install requirements
pip install -r requirements.txt

5. Run the app
streamlit run app.py


The chatbot will be available at:
http://localhost:8501
