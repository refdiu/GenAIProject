import streamlit as st
import requests

# Talk to Ollama
def pm_chatbot(query):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "codellama:7b",  # or "mistral" or any model you pulled
                "prompt": (
                    "You are a helpful AI assistant that explains software project management concepts like "
                    "user stories, backlog, story points, testing strategies, code improvement tips, etc.\n\n"
                    f"User: {query}\nAssistant:"
                ),
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Sorry, I didn't get that.")
    except requests.exceptions.RequestException as e:
        return f"⚠️ Couldn't connect to Ollama: {e}"

# Chatbot UI
def render_pm_chatbot():
    st.title("🤖 PM Chatbot (Ollama Powered)")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    user_input = st.text_input("Ask me anything about PM concepts...")

    if user_input:
        answer = pm_chatbot(user_input)
        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("Bot", answer))

    # Chat history
    for speaker, msg in st.session_state.chat:
        icon = "🧑" if speaker == "You" else "🤖"
        st.markdown(f"**{icon} {speaker}:** {msg}")
