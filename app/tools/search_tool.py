import os
from langchain_community.tools.tavily_search import TavilySearchResults

def get_search_tool():
    """
    Returns the Tavily Search tool. 
    The agent uses this as a fallback to search the web for external knowledge,
    general facts, or recent events if the document_search_tool lacks the answer.
    """
    # Ensure TAVILY_API_KEY is in your .env file
    return TavilySearchResults(max_results=3)