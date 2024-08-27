######################################
# This original code using browserless comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/tools/browser_tools.py 
# This code has been changed to use request
# And is licensed under MIT to comply with the original source
# Chromium Driver: https://googlechromelabs.github.io/chrome-for-testing/ 
######################################
import json
import os

import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html
from textwrap import dedent
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

import platform

#FIXME: May want to change this to headless

class BrowserTools:

    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """Useful to scrape and summarize a website content"""
        if isinstance(website, dict) and "title" in website:
            website = website["title"]

        # Set up Chrome options to run headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=NetworkService")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--log-level=3")  # Enable verbose logging

        # Initialize the Chrome WebDriver
        current_os = platform.system()
        if current_os == "Windows":
            service = Service('chromedriver/chromedriver.exe')  # Specify the path to your chromedriver
        else:
            service = Service('chromedriver/chromedriver')  # Specify the path to your chromedriver
            
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            
            # Navigate to the website
            driver.get(website)

            # Allow time for the page to load and any JavaScript to execute
            time.sleep(3)

            # Get the page source after JavaScript has executed
            page_source = driver.page_source

        finally:
            driver.quit()

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(page_source, 'html.parser')
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
                expected_output="A concise summary of the most relevant information from the provided content."
            )
            summary = task.execute()
            summaries.append(summary)

        return "\n\n".join(summaries)