from app.tools.search_tool import get_search_tool
from app.tools.rag_tool import document_search_tool

def get_all_tools(conversation_id: str):
    """
    Returns a list of all registered LangChain tools for the AI Tutor agent.
    """
    tools = [
        document_search_tool(conversation_id), # Our new RAG tool (Priority 1)
        get_search_tool(),    # Web search fallback (Priority 2)
    ]
    return tools