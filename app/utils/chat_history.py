def build_chat_history(messages, limit=10):
    """
    Convert MongoDB messages to LangChain format.
    Keeps only last N messages to avoid token explosion.
    """
    chat_history = []

    for msg in messages[-limit:]:
        role = msg.get("role")
        content = msg.get("content")

        if role in ["user", "assistant"]:
            chat_history.append((role, content))

    return chat_history