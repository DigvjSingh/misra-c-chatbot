import streamlit as st
from chatbot_engine import ask_bot, extract_text

st.set_page_config(page_title="MISRA C Chatbot", layout="wide")
st.title("Embedded C Chatbot (MISRA + SESD 276)")

uploaded = st.file_uploader("Upload Hardware Datasheet (PDF)", type=["pdf"])
query = st.text_input("Ask for code:")

if st.button("Generate Code"):
    if uploaded and query:
        text = extract_text(uploaded)
        result = ask_bot(query, text)
        st.code(result, language="c")
    elif query:
        result = ask_bot(query, "")
        st.code(result, language="c")
    else:
        st.warning("Enter a query (and optionally upload a datasheet).")
