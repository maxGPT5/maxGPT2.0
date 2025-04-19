import streamlit as st
import requests
import re

# --- App Config ---
st.set_page_config(page_title="maxGPT | AI Chat", layout="centered")

# --- API Keys from Streamlit Secrets ---
API_KEY = st.secrets["api"]["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"]
GOOGLE_API_KEY = st.secrets[""]["AIzaSyABhQ0GlDJXEx3StLHpdi3KjMG7cB7zxzI"]
GOOGLE_CX = st.secrets["api"]["60640d6cf20594547"]

# --- Constants ---
MODEL = "mistralai/mistral-7b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- Initialize Variables ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Styles ---
st.markdown("""
    <style>
        .chat-bubble {
            padding: 0.8rem 1rem;
            border-radius: 1rem;
            margin: 0.5rem 0;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #DCF8C6;
            margin-left: auto;
            text-align: right;
        }
        .ai-bubble {
            background-color: #F1F0F0;
            margin-right: auto;
            text-align: left;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        code {
            background-color: #f5f5f5 !important;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🧠 maxGPT - Chat with AI")

# --- Utility: Detect Search ---
def is_search_command(text):
    return text.strip().lower().startswith("search:")

# --- Google Search ---
def google_search(query):
    search_url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])

        if not items:
            return "❌ No results found."

        results = ""
        for item in items[:5]:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")
            results += f"**[{title}]({link})**\n\n{snippet}\n\n---\n"
        return results.strip()

    except requests.exceptions.RequestException as e:
        return f"❌ Google Search Error: {e}"

# --- Talk to AI ---
def ask_ai(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",
        "X-Title": "Streamlit Chat"
    }

    st.session_state.history.append({"role": "user", "content": user_input})
    payload = {
        "model": MODEL,
        "messages": st.session_state.history
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
        ai_reply = humanize_ai_response(ai_reply)
        st.session_state.history.append({"role": "assistant", "content": ai_reply})
        return ai_reply
    except requests.exceptions.RequestException as e:
        return f"❌ Oops! Something went wrong: {e}. Please try again."

# --- Make AI Sound Human-ish ---
def humanize_ai_response(text):
    text = text.strip()
    if text:
        text = text[0].capitalize() + text[1:]
    text = text.replace("I think", "Hmm, I think...")
    text = text.replace("I don't know", "I'm not totally sure, but I can help you look it up!")
    return text + " 🤔 Let me know if you'd like more info or have further questions!"

# --- Render Markdown / Code Blocks ---
def render_ai_response(text):
    parts = re.split(r"```(?:\w+)?\n", text)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            st.markdown(f"<p style='font-size: 16px;'>{part}</p>", unsafe_allow_html=True)
        else:
            st.code(part.rstrip("`").rstrip(), language="python")

# --- Clear Chat ---
if st.button("🧼 Clear Chat"):
    st.session_state.history = []

# --- Display Chat History ---
if st.session_state.history:
    st.markdown("### 💬 Conversation History")
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-container"><div class="chat-bubble user-bubble"><strong>You:</strong><br>{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f'<div class="chat-container"><div class="chat-bubble ai-bubble"><strong>AI:</strong></div></div>',
                unsafe_allow_html=True
            )
            render_ai_response(msg["content"])

# --- Chat Form ---
with st.form(key="chat_form"):
    st.markdown("### Ask me anything:")
    user_input = st.text_area("You:", height=100, placeholder="Try: search: streamlit tutorial")
    send = st.form_submit_button("Send")

    if send and user_input:
        if is_search_command(user_input):
            query = user_input.replace("search:", "", 1).strip()
            with st.spinner(f"Searching Google for: {query}..."):
                results = google_search(query)
                st.markdown("### 🔍 Google Search Results")
                st.markdown(results, unsafe_allow_html=True)
        else:
            with st.spinner("Thinking... 🤔"):
                ai_response = ask_ai(user_input)
                st.write(f"maxGPT: {ai_response}")
