from duckduckgo_search import DDGS

"""
ddgs.chat() starts a chat session with DuckDuckGo AI.

Args:
    keywords (str): The initial message or question to send to the AI.
    model (str): The model to use: "gpt-4o-mini", "llama-3.3-70b", "claude-3-haiku",
        "o3-mini", "mixtral-8x7b". Defaults to "gpt-4o-mini".
    timeout (int): Timeout value for the HTTP client. Defaults to 30.

Returns:
    str: The response from the AI.
"""
ddgs = DDGS(timeout=20)