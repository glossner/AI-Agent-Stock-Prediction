from crewai import Agent, Task
from textwrap import dedent
from langchain_openai import ChatOpenAI
from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools

from langchain_community.tools import YahooFinanceNewsTool

# Initialize the LLM (e.g., OpenAI GPT model)
gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4"
)

class BollingerAnalysisAgents2:
    def bollinger_bands_investment_advisor(self):
        """
        Returns an agent that analyzes Bollinger Bands data to provide actionable investment advice.
        The agent is expected to make buy/sell suggestions based on whether the stock is overbought or oversold.
        """
        return Agent(
            llm=gpt_model,
            role='Bollinger Bands Investment Advisor',
            goal="""Provide actionable buying or selling suggestions by analyzing Bollinger Bands data 
            and determining whether the stock is overbought, oversold, or trending.""",
            backstory="""As a highly skilled investment advisor, you're specialized in analyzing Bollinger Bands to
            provide clear, actionable investment strategies for your clients.""",
            verbose=True,
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet,
                CalculatorTools.calculate,
                SECTools.search_10q,
                SECTools.search_10k,
                YahooFinanceNewsTool()
            ]
        )

    def bollinger_analysis(self, agent, bollinger_bands):
        """
        Create a new task to analyze Bollinger Bands.
        Args:
            agent: The financial analyst agent responsible for analyzing the Bollinger Bands.
            bollinger_bands (dict): The calculated Bollinger Bands.
        Returns:
            Task: The task object for analyzing Bollinger Bands.
        """
        description = dedent(f"""
            Analyze the provided Bollinger Bands data, which includes the Upper Band, Lower Band, 
            and the Moving Average for the stock. Based on these indicators, assess whether the stock 
            is overbought, oversold, or trending sideways. Additionally, provide insights into any 
            trading opportunities that the bands might suggest.
            Your final answer MUST be a comprehensive report discussing whether the stock is overbought 
            or oversold based on the Bollinger Bands, along with any potential trading opportunities.
            Bollinger Bands Data:
            - Upper Band: {bollinger_bands['Upper Band']}
            - Lower Band: {bollinger_bands['Lower Band']}
            - Moving Average: {bollinger_bands['Moving Average']}
        """)

        # Creating and returning the Task object
        return Task(
            description=description,
            agent=agent,
            expected_output="A report analyzing the Bollinger Bands data with insights into potential trading opportunities."
        )
