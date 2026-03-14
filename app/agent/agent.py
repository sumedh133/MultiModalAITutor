from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import GOOGLE_API_KEY


def get_agent():

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY
    )

    return llm