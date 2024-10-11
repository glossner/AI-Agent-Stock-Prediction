
######################################
# This code comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/tools/search_tools.py 
# And is licensed under MIT
######################################

import json
import os
import requests
from langchain.tools import tool

from newspaper import Article
from newspaper.article import ArticleException
from datetime import datetime  
import platform


class SearchTools():
  @tool("Search the internet")
  def search_internet(query):
    """Useful to search the internet 
    about a a given topic and return relevant results"""
    top_result_to_return = 4
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()['organic']
    string = []
    for result in results[:top_result_to_return]:
      try:
        string.append('\n'.join([
            f"Title: {result['title']}", f"Link: {result['link']}",
            f"Snippet: {result['snippet']}", "\n-----------------"
        ]))
      except KeyError:
        next

    return '\n'.join(string)


  @tool("Search news on the internet")
  def search_news(query, top_result_to_return=4):
      """
      Search news about a company, stock, or any other topic and return relevant results with detailed information,
      including the full text of each news article.
      """

      # Private function
      def scrape_full_article(url):
        """
        Scrape the full text of a news article from the given URL using newspaper3k.
        
        Args:
            url (str): The URL of the news article to scrape.
        
        Returns:
            str: The full text of the article, or an error message if scraping fails.
        """
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
      payload = json.dumps({"q": query})
      headers = {
          'X-API-KEY': os.environ['SERPER_API_KEY'],
          'Content-Type': 'application/json'
      }
      
      try:
          response = requests.post(url, headers=headers, data=payload)
          response.raise_for_status()  # Raise an exception for HTTP errors
      except requests.exceptions.RequestException as e:
          return f"Error: Failed to fetch news from SERPER API. Details: {e}"
      
      try:
          results = response.json().get('news', [])
      except json.JSONDecodeError:
          return "Error: Failed to parse JSON response from SERPER API."
      
      if not results:
          return "No news results found."
      
      formatted_results = []
      for result in results[:top_result_to_return]:
          try:
              title = result.get('title', 'No Title')
              link = result.get('link', 'No Link')
              snippet = result.get('snippet', 'No Snippet')
              source = result.get('source', 'Unknown Source')
              date_str = result.get('date', 'Unknown Date')
              thumbnail = result.get('thumbnail', 'No Image')
              
              # Format the date if it's not 'Unknown Date'
              if date_str != 'Unknown Date':
                  try:
                      # Assuming the date is in ISO format; adjust if different
                      date_obj = datetime.fromisoformat(date_str)
                      
                      if platform.system() == "Windows":
                          formatted_date = date_obj.strftime('%b %#d, %Y')
                      else:
                          formatted_date = date_obj.strftime('%b %-d, %Y')
                  except ValueError:
                      formatted_date = date_str  # Use the original string if parsing fails
              else:
                  formatted_date = date_str
              
              # Scrape the full article text
              full_text = scrape_full_article(link)
              
              # Optionally, truncate the full text to a certain length
              truncated_full_text = (full_text[:500] + '...') if len(full_text) > 500 else full_text
              
              formatted_result = '\n'.join([
                  f"Title: {title}",
                  f"Link: {link}",
                  f"Snippet: {snippet}",
                  f"Source: {source}",
                  f"Date: {formatted_date}",
                  f"Thumbnail: {thumbnail}",
                  f"Full Text: {truncated_full_text}",
                  "\n-----------------"
              ])
              formatted_results.append(formatted_result)
          except KeyError:
              # If any expected key is missing, skip this result
              continue
      
      return '\n'.join(formatted_results)

