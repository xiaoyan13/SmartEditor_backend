"""
https://docs.tavily.com/docs/welcome
"""
import os
from .tavily import TavilyClient

def get_tavilyai_results(keywords, options: dict = {}, max_results=5):
    """
    Get Tavily AI search results based on specified keywords and options.

    Args:
        keywords (str): Keywords for Tavily AI search.
        options:
            urls_included (list[str], optional): URLs to include in the search.
            search_depth (str, optional): Search depth option (default is "advanced").
        max_results: The count of results. Named "max_" because tavilyai may not find enough results.

    Returns:
        dict: Tavily AI search results.
    """

    try:
        client = TavilyClient()
    except Exception as err:
        print(f"Failed to create Tavily client. {err}")
        return None

    include_urls = options.get("urls_included")
    search_depth = options.get("search_depth", "advanced")
    try:
        result = client.search(keywords, 
                search_depth=search_depth, 
                include_answer=True,
                max_results=max_results,
                include_domains=include_urls)
        return result
    except Exception as err:
        print(f"Failed to do Tavily Research: {err}")
    
    return None

def tavily_extract_information(json_data, keyword):
    """
    Extract information from the given JSON based on the specified keyword.

    Args:
        json_data (dict): The JSON data.
        keyword (str): The keyword (title, content, answer, follow-query).

    Returns:
        list or str: The extracted information based on the keyword.
    """
    if keyword == 'titles':
        return [result['title'] for result in json_data['results']]
    elif keyword == 'content':
        return [result['content'] for result in json_data['results']]
    elif keyword == 'answer':
        return json_data['answer']
    elif keyword == 'follow-query':
        return json_data['follow_up_questions']
    else:
        return f"Invalid keyword: {keyword}"
