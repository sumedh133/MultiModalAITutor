def extract_text(message):
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return " ".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict)
        )

    return str(content)