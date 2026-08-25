import os
from typing import List, Dict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

# Accept a few common env var names so this works with the .env style
# from the original test script (GEMINI) as well as more conventional names.
API_KEY = os.getenv("GEMINI") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "No Gemini API key found. Set GEMINI (or GEMINI_API_KEY / GOOGLE_API_KEY) "
        "in your .env file before starting the app."
    )

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

SYSTEM_PROMPT = (
    "You are a helpful, friendly, and knowledgeable AI assistant. You maintain "
    "context across the conversation and give clear, concise, well-structured answers."
)

_llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    google_api_key=API_KEY,
    max_output_tokens=1000,
)


def _extract_text(response) -> str:
    """Gemini responses can return content as a plain string or a list of
    content blocks depending on the model/version — handle both, same as
    the original script did."""
    content = response.content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    return content


def generate_reply(history: List[Dict[str, str]], user_message: str) -> str:
    """
    Generate a context-aware reply.

    history: prior messages for this conversation, in chronological order,
             each shaped like {"role": "user"|"assistant", "content": "..."}.
    user_message: the new message to answer, not yet included in history.
    """
    lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for m in history:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))
    lc_messages.append(HumanMessage(content=user_message))

    response = _llm.invoke(lc_messages)
    return _extract_text(response)
