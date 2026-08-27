import streamlit as st
import requests

# Replace the local IP with your live Render URL
API_BASE_URL = "https://my-chatbot-backend.onrender.com"

st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="wide")

# 1. Initialize Session States
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Helper Functions ---
def fetch_conversations():
    try:
        res = requests.get(f"{API_BASE_URL}/conversations")
        return res.json() if res.status_code == 200 else []
    except requests.exceptions.ConnectionError:
        return []

def load_conversation(conv_id):
    try:
        res = requests.get(f"{API_BASE_URL}/conversations/{conv_id}")
        if res.status_code == 200:
            data = res.json()
            st.session_state.conversation_id = data["id"]
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]} for msg in data.get("messages", [])
            ]
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend.")

def delete_conversation(conv_id):
    try:
        res = requests.delete(f"{API_BASE_URL}/conversations/{conv_id}")
        if res.status_code == 200:
            if st.session_state.conversation_id == conv_id:
                st.session_state.conversation_id = None
                st.session_state.messages = []
            st.rerun()
    except requests.exceptions.ConnectionError:
        st.error("Failed to delete conversation.")

def start_new_chat():
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.rerun()

# --- Sidebar UI: History & Navigation ---
with st.sidebar:
    st.title("💬 Chat History")
    
    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()

    st.divider()

    conversations = fetch_conversations()
    if conversations:
        for conv in conversations:
            col1, col2 = st.columns([0.8, 0.2])
            
            title = conv.get("title") or f"Chat {conv['id'][:8]}"
            if col1.button(f"📝 {title[:20]}...", key=f"load_{conv['id']}", use_container_width=True):
                load_conversation(conv['id'])
                st.rerun()

            if col2.button("🗑️", key=f"del_{conv['id']}"):
                delete_conversation(conv['id'])
    else:
        st.caption("No past conversations found.")

# --- Main Chat UI ---
st.title("🤖 Intelligent Assistant")

# Render active message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"message": prompt}
    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id

    # Send POST request to /chat
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
                
                # Check for successful 200 OK response
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.conversation_id = data["conversation_id"]
                    reply = data["reply"]
                    
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                else:
                    # Safe extraction of backend HTTP error details
                    try:
                        error_detail = response.json().get("detail", response.text)
                    except Exception:
                        error_detail = response.text or "Unknown Server Error"
                    
                    st.error(f"Backend Error [{response.status_code}]: {error_detail}")

            except requests.exceptions.ConnectionError:
                st.error("Error: Could not connect to backend server. Make sure FastAPI is running.")