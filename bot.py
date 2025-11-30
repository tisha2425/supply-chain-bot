

import os
from typing import List

import streamlit as st

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
 
    pass

from langchain_core.messages import HumanMessage, AIMessage


from langchain_google_genai import ChatGoogleGenerativeAI

# Prefer env var, fallback to Streamlit secrets
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY missing. Add it to environment variables or Streamlit Cloud Secrets."
    )


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.65,
)


st.set_page_config(page_title="Supply Chain Risk Bot", page_icon="🔎", layout="centered")


st.markdown(
    """
<style>
/* Animated pastel gradient background (darker pastel palette) */
.stApp {
    background: linear-gradient(135deg,
        #d8c9ff,
        #ffc8d4,
        #fff1b8
    );
    background-size: 400% 400%;
    animation: pastelShift 18s ease infinite;
    font-family: 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial;
    color: #222;
}

/* gradient animation */
@keyframes pastelShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Large centered hero glass box */


/* Title inside hero box */
.hero-title {
    font-size: 44px;
    font-weight: 700;
    margin: 2px 0;
    text-align: center;
}

/* subtitle inside hero box */
.hero-subtitle {
    font-size: 15px;
    color: #666;
    margin-top: 8px;
    text-align: center;
}

/* Chat area (under hero) */
.chat-card {
    width: 78%;
    max-width: 980px;
    margin: 10px auto 40px auto;
    padding: 6px 12px 36px 12px;
    background: transparent;
}

/* Message bubbles - clean glass style */
.user-msg, .ai-msg {
    background: rgba(255,255,255,0.86);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    border-radius: 14px;
    padding: 12px 16px;
    margin: 10px 0;
    max-width: 78%;
    line-height: 1.45;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    color: #222;
}

/* alignment */
.user-msg { margin-left: auto; }
.ai-msg   { margin-right: auto; }

/* Clear floats (not strictly needed for this approach) */
.clearfix { clear: both; }

/* Visual tweak for Streamlit chat input */
textarea[role="textbox"] {
    border-radius: 28px !important;
    padding: 14px !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.04);
}

/* Bottom pinned quote (absolute bottom of page) */
.bottom-footer {
    position: fixed;
    bottom: 10px;   /* adjust if overlapping input on some screens */
    left: 0;
    width: 100%;
    text-align: center;
    z-index: 999;
    pointer-events: none; /* avoid blocking clicks */
}
.bottom-footer .quote-box {
    display: inline-block;
    background: rgba(255,255,255,0.9);
    padding: 10px 18px;
    border-radius: 999px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.08);
    color: #445;
    font-style: italic;
    pointer-events: auto; /* allow hover if needed */
}

/* Responsive */
@media (max-width: 640px) {
    .hero-box { width: 92%; height: 200px; padding: 20px; }
    .chat-card { width: 92%; padding: 10px; }
    .hero-title { font-size: 28px; }
}
</style>
""",
    unsafe_allow_html=True,
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history: List = []


st.markdown('<div class="hero-title">Supply Chain Risk Bot</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Minimal · Aesthetic </div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="chat-card">', unsafe_allow_html=True)


def get_response(query: str, chat_history: List) -> str:
    """
    Call Gemini LLM and return assistant text. Returns a string on success
    or an error string on failure.
    """
    # Build a small readable history (last 8 items)
    history_text = ""
    for msg in chat_history[-8:]:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        content = getattr(msg, "content", str(msg))
        history_text += f"{role}: {content}\n"

    prompt = f"""You are a helpful supply chain risk assistant manager.
Be concise, analytical, and list assumptions when appropriate.

Chat history:
{history_text}

User message:
{query}

Answer clearly; prefer short bullet points or short paragraphs."""
    try:
        # `invoke` accepts a list of messages
        response = llm.invoke([HumanMessage(prompt)])
        # extract content robustly
        if hasattr(response, "content"):
            return response.content
        elif isinstance(response, dict) and "content" in response:
            return response["content"]
        else:
            return str(response)
    except Exception as exc:
        # return readable error string (avoid exposing secrets)
        return f"Error calling Gemini API: {exc}"


for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        st.markdown(f'<div class="user-msg">{message.content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg">{message.content}</div>', unsafe_allow_html=True)
    st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)


user_query = st.chat_input("Type a message...")

if user_query and user_query.strip() != "":

    user_msg = HumanMessage(user_query)
    st.session_state.chat_history.append(user_msg)

    st.markdown(f'<div class="user-msg">{user_query}</div>', unsafe_allow_html=True)
    st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)


    with st.spinner("Thinking..."):
        ai_text = get_response(user_query, st.session_state.chat_history)

    st.markdown(f'<div class="ai-msg">{ai_text}</div>', unsafe_allow_html=True)
    st.markdown('<div class="clearfix"></div>', unsafe_allow_html=True)

   
    st.session_state.chat_history.append(AIMessage(ai_text))


st.markdown('</div>', unsafe_allow_html=True)


st.markdown(
    """
<div class="bottom-footer">
    <div class="quote-box">🌿 “Small risks ignored today become big problems tomorrow.”</div>
</div>
""",
    unsafe_allow_html=True,
)

