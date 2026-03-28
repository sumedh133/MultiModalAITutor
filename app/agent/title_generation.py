from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY

def generate_chat_title(user_message, assistant_response=None):
    
    # low temperature for more deterministic titles, can be adjusted as needed
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )

    prompt = f"""
        Generate a short title (maximum 6 words) for this conversation. You are a title generator for a multimodular ai tutor. The title should be concise, descriptive, and capture the essence of the user's question or topic. There will be docs uploaded which may contain relevant information so refer to the ai tutor's response to the user message for context. The topic of the conversation and the docs uploaded can likely be inferred from the ai tutor's response.

        User question:
        {user_message}
        
        Assistant Response:
        {assistant_response}

        Return ONLY the title.
    """

    response = llm.invoke(prompt)

    return response.content.strip()