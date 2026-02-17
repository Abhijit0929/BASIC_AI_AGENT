import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

# -------------------------
# Load environment
# -------------------------
load_dotenv()

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.9
)

st.title("🤖 Gemini AI Agent")

# -------------------------
# Session state for memory
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# Display old messages
# -------------------------
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    else:
        with st.chat_message("assistant"):
            st.write(msg.content)

# -------------------------
# User input
# -------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Save user message
    st.session_state.chat_history.append(
        HumanMessage(content=user_input)
    )

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = llm.invoke(st.session_state.chat_history)
            st.write(response.content)

    # Save AI message
    st.session_state.chat_history.append(
        AIMessage(content=response.content)
    )
