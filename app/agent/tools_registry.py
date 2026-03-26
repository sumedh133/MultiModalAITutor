from app.tools.search_tool import get_search_tool

def get_all_tools():
    """
    Returns a list of all registered LangChain tools for the agent.
    Add new tools to this list as they are developed.
    """
    tools = [
        get_search_tool(),
    ]
    return tools