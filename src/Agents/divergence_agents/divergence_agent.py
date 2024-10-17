# src/Agents/divergence_agents/divergence_agent.py

from crewai import Agent, Task
from textwrap import dedent
from src.Indicators.detect_divergence import DivergenceDetector  # Import DivergenceDetector
from langchain_openai import ChatOpenAI
from src.Agents.Analysis.Tools.browser_tools import BrowserTools
from src.Agents.Analysis.Tools.calculator_tools import CalculatorTools
from src.Agents.Analysis.Tools.search_tools import SearchTools
from src.Agents.Analysis.Tools.sec_tools import SECTools

# Initialize the LLM (e.g., OpenAI GPT model)
gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4"
)

class DivergenceAnalysisAgents:
    def divergence_trading_advisor(self):
        """
        Returns an agent that interprets divergence signals and provides insights on potential market reversals.
        """
        return Agent(
            llm=gpt_model,
            role='Divergence Trading Advisor',
            goal="""Analyze divergence signals detected in MACD and RSI and provide insights into 
            potential reversals by analyzing historical data.""",
            backstory="""As an expert in market analysis, this agent specializes in confirming divergence 
            patterns to avoid false signals and improve trade accuracy.""",
            verbose=True,
            tools=[
                BrowserTools.scrape_and_summarize_website,
                SearchTools.search_internet,
                CalculatorTools.calculate,
                SECTools.search_10q,
                SECTools.search_10k
            ]
        )

class DivergenceAnalysisTasks:
    def detect_divergence(self, agent, price_data, indicator_data, indicator_name):
        """
        Detect potential divergence signals and create a task for ChatGPT analysis.

        Args:
            agent: The Divergence Trading Advisor agent.
            price_data (pd.DataFrame): The stock price data.
            indicator_data (pd.DataFrame): The indicator data (MACD/RSI).
            indicator_name (str): Name of the indicator used for divergence detection.

        Returns:
            Task: A task for ChatGPT to analyze the divergence.
        """
        # Detect divergence using DivergenceDetector
        detector = DivergenceDetector(price_data, indicator_data, indicator_name)
        bullish_divergences = detector.detect_bullish_divergence()
        bearish_divergences = detector.detect_bearish_divergence()

        # Create a message for ChatGPT analysis
        market_context = "Bullish trend" if len(bullish_divergences) > len(bearish_divergences) else "Bearish trend"
        description = dedent(f"""
            Detected divergence in {indicator_name} on the following dates:
            Bullish Divergences: {', '.join([str(d) for d in bullish_divergences])}
            Bearish Divergences: {', '.join([str(d) for d in bearish_divergences])}

            Market context: {market_context}.
            Please analyze these divergence signals to confirm if they indicate a potential market reversal.
        """)

        return Task(
            description=description,
            agent=agent,
            expected_output="A detailed analysis of the divergence signals with a recommendation."
        )
