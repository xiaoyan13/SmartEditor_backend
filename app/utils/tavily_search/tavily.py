import requests
import json
import os
from typing import Literal, Sequence, Optional, List, Union
from .errors import UsageLimitExceededError, InvalidAPIKeyError, MissingAPIKeyError, BadRequestError


class TavilyClient:
    """
    Tavily API client class.
    """

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise MissingAPIKeyError()
        self.base_url = "https://api.tavily.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
        }

    def _search(self,
                query: str,
                search_depth: Literal["basic", "advanced"] = "basic",
                topic: Literal["general", "news"] = "general",
                days: int = 3,
                max_results: int = 5,
                include_domains: Sequence[str] = None,
                exclude_domains: Sequence[str] = None,
                include_answer: bool = False,
                include_raw_content: bool = False,
                include_images: bool = False,
                **kwargs
                ) -> dict:
        """
        Internal search method to send the request to the API.
        """

        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
            "api_key": self.api_key,
        }

        if kwargs:
            data.update(kwargs)

        response = requests.post(self.base_url + "/search", data=json.dumps(data), headers=self.headers, timeout=100)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            detail = 'Too many requests.'
            try:
                detail = response.json()['detail']['error']
            except:
                pass

            raise UsageLimitExceededError(detail)
        elif response.status_code == 401:
            raise InvalidAPIKeyError()
        else:
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code

    def search(self,
               query: str,
               search_depth: Literal["basic", "advanced"] = "basic",
               topic: Literal["general", "news"] = "general",
               days: int = 3,
               max_results: int = 5,
               include_domains: list[str] = None,
               exclude_domains: Sequence[str] = None,
               include_answer: bool = False,
               include_raw_content: bool = False,
               include_images: bool = False,
               **kwargs,  # custom arguments
               ) -> dict:
        """
        Combined search method.
        """

        response_dict = self._search(query,
                                     search_depth=search_depth,
                                     topic=topic,
                                     days=days,
                                     max_results=max_results,
                                     include_domains=include_domains,
                                     exclude_domains=exclude_domains,
                                     include_answer=include_answer,
                                     include_raw_content=include_raw_content,
                                     include_images=include_images,
                                     **kwargs,
                                     )

        tavily_results = response_dict.get("results", [])

        response_dict["results"] = tavily_results

        return response_dict

    def _extract(self,
                 urls: Union[List[str], str],
                 **kwargs
                 ) -> dict:
        """
        Internal extract method to send the request to the API.
        """
        data = {
            "urls": urls,
            "api_key": self.api_key
        }
        if kwargs:
            data.update(kwargs)

        response = requests.post(self.base_url + "/extract", data=json.dumps(data), headers=self.headers, timeout=100)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            detail = 'Bad request. The request was invalid or cannot be served.'
            try:
                detail = response.json()['detail']['error']
            except KeyError:
                pass
            raise BadRequestError(detail)
        elif response.status_code == 401:
            raise InvalidAPIKeyError()
        elif response.status_code == 429:
            detail = 'Too many requests.'
            try:
                detail = response.json()['detail']['error']
            except:
                pass
            raise UsageLimitExceededError(detail)
        else:
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code

    def extract(self,
                urls: Union[List[str], str],  # Accept a list of URLs or a single URL
                **kwargs,  # Accept custom arguments
                ) -> dict:
        """
        Combined extract method.
        """
        response_dict = self._extract(urls,
                                      **kwargs)

        tavily_results = response_dict.get("results", [])
        failed_results = response_dict.get("failed_results", [])

        response_dict["results"] = tavily_results
        response_dict["failed_results"] = failed_results

        return response_dict
