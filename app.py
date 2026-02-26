import streamlit as st
import os 
import requests
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
    temperature=0.8
)

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(layout="wide")
st.title("🤖 AI Agent Suite")

# -----------------------------------
# Tabs (MAIN FEATURE)
# -----------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📄 PDF AI Agent", "✈️ Trip Planner Agent", "🎬 Movie Agent"]
)

# =====================================================
# 📄 TAB 1 — PDF ANALYSIS AGENT
# =====================================================
with tab1:

    st.header("📄 Gemini PDF Analysis Chat")

    # Session State
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar Upload
    st.sidebar.header("Upload PDF")

    uploaded_pdf = st.sidebar.file_uploader(
        "Upload a PDF",
        type="pdf"
    )

    # Extract PDF Text
    def extract_pdf_text(pdf_file):
        reader = PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text

    # Store PDF
    if uploaded_pdf:
        pdf_text = extract_pdf_text(uploaded_pdf)
        st.session_state["pdf_text"] = pdf_text
        st.sidebar.success("PDF loaded successfully!")

    # Show Chat History
    for msg in st.session_state.chat_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(msg.content)

    # Chat Input
    user_input = st.chat_input("Ask about your PDF...")

    if user_input:

        with st.chat_message("user"):
            st.write(user_input)

        st.session_state.chat_history.append(
            HumanMessage(content=user_input)
        )

        context = ""

        if "pdf_text" in st.session_state:
            context = f"""
You are helping analyze a PDF.

PDF CONTENT:
{st.session_state["pdf_text"][:8000]}
"""

        full_prompt = context + "\nUser question: " + user_input

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = llm.invoke(full_prompt)
                st.write(response.content)

        st.session_state.chat_history.append(
            AIMessage(content=response.content)
        )

# =====================================================
# ✈️ TAB 2 — TRIP PLANNER AGENT
# =====================================================
with tab2:

    st.header("✈️ AI Trip Planner Agent")

    # Session State
    if "final_plan" not in st.session_state:
        st.session_state.final_plan = ""

    if "thinking" not in st.session_state:
        st.session_state.thinking = ""

    # Agent Function
    def trip_planner_agent(destination, days, budget, interests):

        interests_text = ", ".join(interests) if interests else "General tourism"

        prompt = f"""
You are an expert AI Travel Planner Agent.

Destination: {destination}
Days: {days}
Budget: {budget}
Interests: {interests_text}

Follow process:

1. Think step-by-step
2. Optimize schedule
3. Suggest realistic locations
4. Provide travel tips

Return EXACT format:

THINKING:
(reasoning)

FINAL ITINERARY:
(day-wise plan)
"""

        response = llm.invoke(prompt)
        return response.content

    # Columns Layout
    col1, col2, col3 = st.columns([1, 1, 2])

    # LEFT COLUMN — INPUT
    with col1:
        st.subheader("🧭 Trip Details")

        destination = st.text_input("Destination")

        days = st.number_input(
            "Number of Days",
            1, 30, 3
        )

        budget = st.selectbox(
            "Budget",
            ["Low", "Medium", "Luxury"]
        )

        interests = st.multiselect(
            "Interests",
            ["Food", "Nature", "Adventure", "History", "Shopping", "Nightlife"]
        )

        generate_plan = st.button("Generate Plan")

    # Generate Plan
    if generate_plan and destination:

        with st.spinner("Planning your trip..."):
            result = trip_planner_agent(
                destination,
                days,
                budget,
                interests
            )

            if "FINAL ITINERARY:" in result:
                thinking, final_plan = result.split("FINAL ITINERARY:")
                thinking = thinking.replace("THINKING:", "").strip()

                st.session_state.thinking = thinking
                st.session_state.final_plan = final_plan.strip()
            else:
                st.session_state.final_plan = result

    # MIDDLE COLUMN — THINKING
    with col2:
        st.subheader("🤖 Agent Reasoning")

        if st.session_state.thinking:
            st.write(st.session_state.thinking)
        else:
            st.info("Agent reasoning will appear here.")

    # RIGHT COLUMN — PLAN
    with col3:
        st.subheader("🗺 Trip Plan")

        if st.session_state.final_plan:
            st.write(st.session_state.final_plan)
        else:
            st.info("Generate a trip to see itinerary.")
  
  
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def get_movie_poster(movie_name):
    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name
    }

    response = requests.get(url, params=params).json()

    if response["results"]:
        poster_path = response["results"][0]["poster_path"]
        rating = response["results"][0]["vote_average"]

        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return poster_url, rating

    return None, None          
            
# =====================================================
# 🎬 TAB 3 — MOVIE SUGGESTION AGENT
# =====================================================
with tab3:

    st.header("🎬 Movie Suggestion AI Agent")

    if "movie_results" not in st.session_state:
        st.session_state.movie_results = ""

    # Movie Agent Function
    def movie_agent(genre, mood, language, min_rating):
        prompt = f"""
Suggest 5 movies.

Genre: {genre}
Mood: {mood}
Language: {language}
Minimum IMDb Rating: {min_rating}

Return ONLY movie names separated by commas.
    """ 
        response = llm.invoke(prompt)
        return response.content

    # UI Layout
    colA, colB = st.columns([1,2])

    # LEFT — INPUTS
    with colA:
        st.subheader("🎥 Preferences")

    # ---- Row 1 ----
    c1, c2 = st.columns(2)

    with c1:
        genre = st.selectbox(
            "Genre",
            ["Action", "Comedy", "Sci-Fi", "Romance", "Thriller", "Horror", "Drama"]
        )

    with c2:
        mood = st.selectbox(
            "Mood",
            ["Happy", "Excited", "Emotional", "Relaxed", "Dark", "Motivational"]
        )

    # ---- Row 2 ----
    c3, c4 = st.columns(2)

    with c3:
        language = st.selectbox(
            "Language",
            ["English", "Hindi", "Marathi", "Japanese"]
        )

    with c4:
        min_rating = st.slider(
            "Minimum IMDb Rating",
            5.0, 9.5, 7.0
        )

    # ---- Center Button ----
    st.markdown("<br>", unsafe_allow_html=True)

    recommend_btn = st.button(
        "🎬 Recommend Movies",
        use_container_width=True
    )

    # RIGHT — RESULTS
    if recommend_btn:
        with st.spinner("Fetching movies..."):
            movies_text = movie_agent(
            genre, mood, language, min_rating
        )

        movie_list = [m.strip() for m in movies_text.split(",")]

        cols = st.columns(5)

        for i, movie in enumerate(movie_list[:5]):

            poster, rating = get_movie_poster(movie)

            with cols[i]:
                if poster:
                    st.image(poster, use_container_width=True)
                st.markdown(f"**{movie}**")
                if rating:
                    st.write(f"⭐ TMDB Rating: {rating}")