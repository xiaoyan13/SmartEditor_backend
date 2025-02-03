import os
import json
import requests

def do_google_serp_search(search_keywords, config=[]):
    """ Common function to do google SERP analysis and return results. """

    try:
        # todo: extract search params from config
        geo_loc = 'cn'
        lang = 'zh-cn'
        num_results = 5
        
        g_results = perform_serperdev_google_search(search_keywords, geo_loc, lang, num_results)
        return g_results
    except Exception as e:
        print(e)
        return None
    

def perform_serperdev_google_search(keywords, geo_loc, lang, num_results):
    """
    Perform a Google search using the Serper API.

    Args:
        query (str): The search query.

    Returns:
        dict: The JSON response from the Serper API.
    """
    # Get the Serper API key from environment variables
    serper_api_key = os.getenv('SERPER_API_KEY')

    # Check if the API key is available
    if not serper_api_key:
        raise ValueError("SERPER_API_KEY is missing. Set it in the .env file.")

    # Serper API endpoint URL
    url = "https://google.serper.dev/search"

    # Build payload as end user or main_config
    payload = json.dumps({
        "q": keywords,
        "gl": geo_loc,
        "hl": lang,
        "num": num_results,
        "autocorrect": True,
    })

    # Request headers with API key
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    # Send a POST request to the Serper API
    response = requests.post(url, headers=headers, data=payload, stream=True)
    # Check if the request was successful
    if response.status_code == 200:
        # Parse and return the JSON response
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    print(do_google_serp_search("hello world"))