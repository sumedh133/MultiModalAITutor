def extract_text(result):
    output = result.get("output")

    # Case 1: already a string
    if isinstance(output, str):
        return output

    # Case 2: list of blocks
    if isinstance(output, list):
        return " ".join(
            block.get("text", "")
            for block in output
            if isinstance(block, dict)
        )

    return str(result)