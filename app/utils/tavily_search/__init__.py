from .funcs import get_tavilyai_results, tavily_extract_information

def do_tavily_ai_search(search_keywords, options: dict = {}, return_count=10):
    """ Common function to do Tavily AI web research."""
    try:
        print(f"Doing Tavily AI search for: {search_keywords}")
        t_results = get_tavilyai_results(search_keywords, options, max_results=return_count)
        t_titles = tavily_extract_information(t_results, 'titles')
        t_answer = tavily_extract_information(t_results, 'answer')
        print('Tavily returned the result successfully.')
        return (t_results, t_titles, t_answer)
    except Exception as err:
        print(f"Failed to do Tavily AI Search: {err}")
        

