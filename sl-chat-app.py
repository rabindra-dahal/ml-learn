import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# 1. Force load the .env file immediately
load_dotenv()

# 2. Page Configuration
st.set_page_config(page_title="My Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 My AI Chatbot")
st.caption("Powered by Google GenAI Chats, Streamlit, and dotenv")

# 3. Retrieve the API key explicitly
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Missing `GEMINI_API_KEY`. Please ensure you have a file exactly named `.env` in this directory containing: `GEMINI_API_KEY=your_key_here`")
    st.stop()

# 4. Initialize the client by passing the key explicitly to bypass environment issues
@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

client = get_gemini_client(api_key)

# 5. Initialize Gemini Chat Session in Streamlit Session State
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(model="gemini-3.6-flash")

# 6. Display Previous Chat Messages
for message in st.session_state.chat_session.get_history():
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        if message.parts:
            st.markdown(message.parts[0].text)

# 7. Accept User Input
if user_prompt := st.chat_input("What is on your mind?"):
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Send message and stream the response via recommended Chat API
            response_stream = st.session_state.chat_session.send_message_stream(
                user_prompt
            )
            
            for chunk in response_stream:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
