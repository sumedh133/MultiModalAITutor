from langchain_core.tools import StructuredTool
from app.rag.retriever import get_answer_from_documents


def document_search_tool(conversation_id: str):
    """
    Creates a conversation-specific document search tool
    """

    def _search(query: str) -> str:
        try:
            return get_answer_from_documents(
                query=query,
                conversation_id=conversation_id
            )
        except Exception as e:
            return f"Could not retrieve documents. Error: {e}"

    return StructuredTool.from_function(
        func=_search,
        name="document_search",
        description=(
            "Use this FIRST to answer questions about the user's uploaded "
            "study materials, notes, textbooks, or concepts."
        )
    )

