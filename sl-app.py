import os
import streamlit as st
from google import genai

from dotenv import load_dotenv

# Load variables from the .env file into the system environment
load_dotenv()


# 1. Page Configuration & Title
st.set_page_config(page_title="Gemini 3.6 Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Gemini 3.6 Flash Chat")
st.caption("A simple GenAI app powered by Google GenAI and Streamlit")

# 2. Check for API Key
if not os.getenv("GEMINI_API_KEY"):
    st.error("Missing `GEMINI_API_KEY` environment variable. Please set it in your terminal and restart the app.")
    st.stop()

# 3. Initialize the Gemini Client
@st.cache_resource
def get_gemini_client():
    return genai.Client()

client = get_gemini_client()

# 4. Initialize Streamlit Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display Previous Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Accept User Input
if user_prompt := st.chat_input("What is on your mind?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Display assistant response in chat message container with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Generate the content streaming from gemini-3.6-flash
            response_stream = client.models.generate_content_stream(
                model='gemini-3.6-flash',
                contents=user_prompt
            )
            
            # Stream the response chunk by chunk to the UI
            for chunk in response_stream:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            # Remove the cursor block element once done
            message_placeholder.markdown(full_response)
            
            # Add assistant response to session state chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
