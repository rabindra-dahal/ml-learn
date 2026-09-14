import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load environment variables
load_dotenv()

# 2. UI Layout Configuration
st.set_page_config(page_title="MyNep Telecom AI Helpdesk + Tools", page_icon="📞", layout="wide")

st.title("📞 MyNep Telecom Live Support Engine")
st.caption("Powered by Gemini 3.6 Flash with Live Tool Execution & Scenario Injection")

# 3. Secure API Key Retrieval
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ `GEMINI_API_KEY` not detected. Please verify your local `.env` file configuration.")
    st.stop()

# 4. Initialize SDK Client
@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

client = get_gemini_client(api_key)

# ==========================================
# FEATURE 1: PYTHON TOOLS FOR GENAI (AFC)
# ==========================================
def check_user_account_balance() -> str:
    """
    Looks up the current customer's active account balance, payment due dates, and data usage statistics.
    Returns a string containing the current statement status.
    """
    # In a real app, this would query an internal billing SQL database or API
    return (
        "Account Status: ACTIVE\n"
        "- Current Outstanding Balance: $74.50\n"
        "- Payment Due Date: October 5, 2026\n"
        "- Data Allowance: 42GB used out of 50GB (8GB remaining on 5G Core Profile)"
    )

def execute_remote_router_reboot() -> str:
    """
    Triggers an automated hardware diagnostic and remote firmware power-cycle (reboot) sequence on the customer's fiber home gateway.
    Returns the technical execution log output string.
    """
    # Simulating standard network firmware protocols
    return (
        "SUCCESS: Gateway connection ping dropped... Sending hard power-cycle command... "
        "Booting firmware v4.12... Resyncing DSL channels... Line health status: 100% stable. "
        "The router was successfully rebooted and is now back online with optimal throughput."
    )

# ==========================================
# SETUP PERSISTENT CONTEXT & PERSONA
# ==========================================
HELPDESK_PROMPT = """
You are an expert customer support agent for 'MyNep Telecom'.
Your goal is to assist customers with patience, empathy, and technical expertise.

You have access to internal automated diagnostic tools:
1. `check_user_account_balance`: Use this immediately when users ask about their bills, fees, balance, or data allowances.
2. `execute_remote_router_reboot`: Use this if a user reports slow internet, Wi-Fi connectivity dropouts, or broadband network errors. Explain to them that you are running a remote line reset before invoking the tool.

Operational Rule: Do not invent mock technical statuses or balances out of nowhere. Always use the explicit outputs returned from your tools.
"""

# ==========================================
# FEATURE 2: SIDEBAR SCENARIO INJECTOR
# ==========================================
with st.sidebar:
    st.header("🎯 Simulation Control Panel")
    st.subheader("Inject Customer Scenarios")
    st.write("Click a scenario below to instantly populate the customer's chat pipeline:")
    
    # Store standard tickets to save user typing time
    scenarios = {
        "📉 Dropdown: Network Issues": "My fiber broadband has been crawling for three hours and standard websites won't load.",
        "💳 Dropdown: Billing Discrepancy": "Can you check how much money I owe this month? I think my bill is higher than usual.",
        "✈️ Dropdown: Roaming Assistance": "I'm travelling to Europe next week. Will my 5G data plan still function out there?"
    }
    
    injected_prompt = None
    for label, prompt_text in scenarios.items():
        if st.button(label, use_container_width=True):
            injected_prompt = prompt_text

# Initialize chat session with function registration
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-3.6-flash",
        config=types.GenerateContentConfig(
            system_instruction=HELPDESK_PROMPT,
            temperature=0.2,
            # Registering tools natively tells the SDK to listen for AFC requests 
            tools=[check_user_account_balance, execute_remote_router_reboot]
        )
    )

# Render Chat History layout columns
chat_container = st.container()

with chat_container:
    # Safely unpack internal history structures (filters out tool backend logs seamlessly)
    for message in st.session_state.chat_session.get_history():
        role = "user" if message.role == "user" else "assistant"
        if message.parts and len(message.parts) > 0:
            text_content = ""
            for part in message.parts:
                if part.text:
                    text_content += part.text
            if text_content.strip():
                with st.chat_message(role):
                    st.markdown(text_content)

# Process message sequence
user_input = st.chat_input("Ask support a question...")

# Override input string if sidebar simulation click was intercepted
if injected_prompt:
    user_input = injected_prompt

if user_input:
    # 1. Immediately print user input to chat interface
    with chat_container:
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # 2. Call send_message_stream. The SDK intercepts requirements, executes Python 
                # functions implicitly, and passes text outputs back down the pipeline seamlessly.
                response_stream = st.session_state.chat_session.send_message_stream(user_input)
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                        
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"Helpdesk connection fault: {e}")
