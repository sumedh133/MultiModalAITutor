from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY
import base64
import mimetypes


def _get_llm(temperature=0.2):
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=temperature
    )


# -------------------------------
# 🏷️ CHAT TITLE GENERATOR
# -------------------------------
def generate_chat_title(user_message, assistant_response=None):
    llm = _get_llm(temperature=0.2)

    assistant_response = assistant_response or ""

    prompt = f"""
Generate a concise conversation title (max 6 words).

Rules:
- Maximum 6 words
- No quotes
- No punctuation at the end
- Be specific and meaningful
- Prefer nouns and key topics

User:
{user_message}

Assistant:
{assistant_response}

Return only the title.
"""

    response = llm.invoke(prompt)
    title = response.content.strip()

    # 🧹 Hard safety cleanup
    title = title.replace('"', '').replace("'", "").strip()
    title_words = title.split()

    if len(title_words) > 6:
        title = " ".join(title_words[:6])

    return title


# -------------------------------
# 🖼️ IMAGE PROCESSOR (GEMINI VISION)
# -------------------------------
import base64
import mimetypes


def process_image(image_path):
    llm = _get_llm(temperature=0.1)

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/png"

    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    prompt = """
Extract and structure all useful information from this image.

Instructions:
- Extract all readable text
- Clean formatting
- Organize into sections
- Explain diagrams if present
- Keep concise but complete
"""

    response = llm.invoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{image_base64}",
                },
            ],
        }
    ])

    return response.content.strip()