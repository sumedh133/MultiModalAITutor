from langchain_core.tools import tool
from app.rag.retriever import get_answer_from_documents

@tool
def document_search_tool(query: str) -> str:
    """
    ALWAYS use this tool FIRST to answer questions about the user's uploaded 
    study materials, notes, textbooks, or specific concepts they are learning.
    Input should be the student's question.
    """
    try:
        response = get_answer_from_documents(query)
        return response
    except Exception as e:
        return f"Could not retrieve documents. Error: {e}"