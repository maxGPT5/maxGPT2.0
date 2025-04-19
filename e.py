import streamlit as st
import requests
import re

# --- App Config ---
st.set_page_config(page_title="maxGPT | AI Chat", layout="centered")

# --- Constants ---
API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
GOOGLE_API_KEY = "AIzaSyABhQ0GlDJXEx3StLHpdi3KjMG7cB7zxzI"  # 🔑 Add your Google Custom Search API key here
GOOGLE_CX = "60640d6cf20594547"       # 🔑 Add your Google Custom Search Engine ID here

# --- Initialize Variables ---
history = []
input_text = ""

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

# --- Utility: Check for "search:" command ---
def is_search_command(input_text):
    return input_text.strip().lower().startswith("search:")

# --- Google Search Function ---
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
        data = response.json()
        items = data.get("items", [])

        if not items:
            return "❌ No results found. Maybe try rephrasing?"

        formatted_results = ""
        for item in items[:5]:
            title = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet")
            formatted_results += f"**[{title}]({link})**\n\n{snippet}\n\n---\n"

        return formatted_results.strip()

    except requests.exceptions.RequestException as e:
        return f"❌ Google Search Error: {e}"

# --- Ask AI Function ---
def ask_ai(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",
        "X-Title": "Streamlit Chat"
    }

    history.append({"role": "user", "content": user_input})

    payload = {
        "model": MODEL,
        "messages": history
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"]
        humanized_reply = humanize_ai_response(ai_reply)
        history.append({"role": "assistant", "content": humanized_reply})
        return humanized_reply
    except requests.exceptions.RequestException as e:
        return f"❌ Oops! Something went wrong: {e}. Please try again."

# --- Make AI Sound More Human ---
def humanize_ai_response(response_text):
    response_text = response_text.strip()
    if response_text:
        response_text = response_text[0].capitalize() + response_text[1:]
    response_text = response_text.replace("I think", "Hmm, I think...")
    response_text = response_text.replace("I don't know", "I'm not totally sure, but I can help you look it up!")
    response_text += " 🤔 Let me know if you'd like more info or have further questions!"
    if len(response_text) > 150:
        response_text = f"\n{response_text}"
    return response_text

# --- Render AI Markdown / Code ---
def render_ai_response(text):
    parts = re.split(r"```(?:\w+)?\n", text)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            st.markdown(f"<p style='font-size: 16px;'>{part}</p>", unsafe_allow_html=True)
        else:
            code = part.rstrip("`").rstrip()
            st.code(code, language="python")

# --- Clear Chat Button ---
if st.button("🧼 Clear Chat"):
    history = []  # Reset chat history

# --- Chat History Rendering ---
if history:
    st.markdown("### 💬 Conversation History")
    for msg in history:
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

# --- Chat Input Form ---
with st.form(key="chat_input_form"):
    st.markdown("### What can I help you with today?")
    input_text = st.text_area("You:", height=100, placeholder="Ask me anything... or try: search: python tutorial")
    send_button = st.form_submit_button("Send")

    if send_button and input_text:
        if is_search_command(input_text):
            search_query = input_text.replace("search:", "", 1).strip()
            with st.spinner(f"Searching Google for: {search_query}..."):
                results = google_search(search_query)
                st.markdown("### 🔍 Google Search Results")
                st.markdown(results, unsafe_allow_html=True)
        else:
            with st.spinner("Thinking... 🤔"):
                ai_response = ask_ai(input_text)
                if ai_response and "I don't know" in ai_response:
                    with st.spinner(f"Searching Google for: {input_text.strip()}..."):
                        results = google_search(input_text.strip())
                        st.markdown("### 🔍 Google Search Results")
                        st.markdown(results, unsafe_allow_html=True)
                else:
                    st.write(f"maxGPT: {ai_response}")
