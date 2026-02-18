import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from pypdf import PdfReader

# -----------------------------------
# Load environment variables
# -----------------------------------
load_dotenv()

# -----------------------------------
# Gemini Model
# -----------------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.9
)

# -----------------------------------
# Page UI
# -----------------------------------
st.title("🤖 Gemini AI Agent + PDF Analysis")

# -----------------------------------
# Session State (Chat Memory)
# -----------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------
# PDF Upload Section
# -----------------------------------
st.sidebar.header("📄 PDF Analysis")

uploaded_pdf = st.sidebar.file_uploader(
    "Upload a PDF",
    type="pdf"
)

# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text

# Store PDF content
if uploaded_pdf:
    pdf_text = extract_pdf_text(uploaded_pdf)
    st.session_state["pdf_text"] = pdf_text
    st.sidebar.success("PDF loaded successfully!")

# -----------------------------------
# Show previous chat messages
# -----------------------------------
for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.write(msg.content)

# -----------------------------------
# Chat Input
# -----------------------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Save user message
    st.session_state.chat_history.append(
        HumanMessage(content=user_input)
    )

    # -----------------------------------
    # Build prompt with PDF context (if exists)
    # -----------------------------------
    context = ""

    if "pdf_text" in st.session_state:
        context = f"""
You are helping the user analyze a PDF document.

PDF CONTENT:
{st.session_state["pdf_text"][:8000]}
"""

    full_prompt = context + "\nUser question: " + user_input

    # -----------------------------------
    # AI Response
    # -----------------------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.invoke(full_prompt)
            st.write(response.content)

    # Save AI response
    st.session_state.chat_history.append(
        AIMessage(content=response.content)
    )
