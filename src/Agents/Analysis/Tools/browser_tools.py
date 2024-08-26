######################################
# This original code using browserless comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/tools/browser_tools.py 
# This code has been changed to use request
# And is licensed under MIT to comply with the original source
######################################
import json
import os

import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html
from textwrap import dedent
import requests
from bs4 import BeautifulSoup

#TODO: Change the web scraper to Chromium

class BrowserTools:

    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """Useful to scrape and summarize a website content"""
        # Ensure the website input is a string URL
        if isinstance(website, dict) and "title" in website:
            website = website["title"]

        response = requests.get(website)
        if response.status_code != 200:
            return f"Failed to retrieve content from {website}"

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(text=True)

        content = "\n\n".join([str(el) for el in elements])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]

        summaries = []
        for chunk in content:
            agent = Agent(
                role='Principal Researcher',
                goal='Do amazing research and summaries based on the content you are working with',
                backstory="You're a Principal Researcher at a big company and you need to do research about a given topic.",
                allow_delegation=False
            )
            task = Task(
                agent=agent,
                description=dedent(f"""
                    Analyze and summarize the content below, make sure to include the most relevant information in the summary, return only the summary nothing else.
                    
                    CONTENT
                    ----------
                    {chunk}
                """),
                expected_output="A concise summary of the key points extracted from the content."
            )
            summary = task.execute()
            summaries.append(summary)

        return "\n\n".join(summaries)
