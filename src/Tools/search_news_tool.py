
import re
from textwrap import dedent
import crewai as crewai
from datetime import datetime
import os
from src.Agents.base_agent import BaseAgent
import json
import requests
from newspaper import Article
from newspaper.article import ArticleException
from datetime import datetime
import platform
from pydantic import BaseModel, Field, ValidationError
from typing import List
from crewai_tools import BaseTool
from crewai_tools import BaseTool

# Define input and output models for search_news
class SearchNewsInput(BaseModel):
    query: str = Field(..., description="Search term for the news articles.")
    top_result_to_return: int = Field(4, ge=1, le=10, description="Number of top results to return, between 1 and 10.")

class ArticleOutput(BaseModel):
    title: str
    link: str
    snippet: str
    source: str
    date: str
    thumbnail: str
    full_text: str

class SearchNewsOutput(BaseModel):
    results: List[ArticleOutput]


# Tool for searching news with Pydantic validation
class SearchNewsTool(BaseTool):
    name: str = "Search News"
    description: str = "Tool to search news articles about a company, stock, or topic and return detailed results."

    def _run(self, input_data: SearchNewsInput) -> SearchNewsOutput:
        
        def scrape_full_article(url: str) -> str:
            try:
                article = Article(url)
                article.download()
                article.parse()
                return article.text
            except ArticleException as e:
                return f"Error: Failed to scrape the article. Details: {e}"
            except Exception as e:
                return f"Error: An unexpected error occurred while scraping the article. Details: {e}"

        url = "https://google.serper.dev/news"
        payload = json.dumps({"q": input_data.query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to fetch news from SERPER API. Details: {e}"
        
        try:
            results = response.json().get('news', [])
        except json.JSONDecodeError:
            return "Error: Failed to parse JSON response from SERPER API."
        
        if not results:
            return SearchNewsOutput(results=[])

        formatted_results = []
        for result in results[:input_data.top_result_to_return]:
            title = result.get('title', 'No Title')
            link = result.get('link', 'No Link')
            snippet = result.get('snippet', 'No Snippet')
            source = result.get('source', 'Unknown Source')
            date_str = result.get('date', 'Unknown Date')
            thumbnail = result.get('thumbnail', 'No Image')
            
            if date_str != 'Unknown Date':
                try:
                    date_obj = datetime.fromisoformat(date_str)
                    formatted_date = date_obj.strftime('%b %#d, %Y') if platform.system() == "Windows" else date_obj.strftime('%b %-d, %Y')
                except ValueError:
                    formatted_date = date_str
            else:
                formatted_date = date_str
            
            full_text = scrape_full_article(link)
            truncated_full_text = (full_text[:500] + '...') if len(full_text) > 500 else full_text

            formatted_results.append(
                ArticleOutput(
                    title=title,
                    link=link,
                    snippet=snippet,
                    source=source,
                    date=formatted_date,
                    thumbnail=thumbnail,
                    full_text=truncated_full_text
                )
            )

        return SearchNewsOutput(results=formatted_results)