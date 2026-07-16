import ollama

MODEL_NAME = "llama3.2"

SYSTEM_PROMPT = (
    "You are a helpful, friendly AI phone assistant for VoiceOps. "
    "Keep your responses short and conversational, ideally one to two sentences, "
    "since this is a spoken phone conversation, not a text chat. "
    "Do not use markdown, bullet points, or any text formatting - speak naturally."
)


def generate_response(user_text: str) -> str:
    """
    Sends the caller's transcribed speech to the local LLM
    and returns a short, spoken-style reply.
    """
    result = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )
    return result["message"]["content"].strip()