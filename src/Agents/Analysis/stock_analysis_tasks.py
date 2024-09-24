######################################
# This code comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/stock_analysis_tasks.py 
# And is licensed under MIT
######################################


from crewai import Task
from textwrap import dedent
from src.Indicators.detect_divergence import DivergenceDetector
class StockAnalysisTasks():
    def research(self, agent, company):
        return Task(
            description=dedent(f"""
                Collect and summarize recent news articles, press
                releases, and market analyses related to the stock and
                its industry.
                Pay special attention to any significant events, market
                sentiments, and analysts' opinions. Also include upcoming 
                events like earnings and others.
          
                Your final answer MUST be a report that includes a
                comprehensive summary of the latest news, any notable
                shifts in market sentiment, and potential impacts on 
                the stock.
                Also make sure to return the stock ticker.
                
                {self.__tip_section()}
          
                Make sure to use the most recent data as possible.
          
                Selected company by the customer: {company}
            """),
            agent=agent,
            expected_output="A comprehensive report summarizing the latest news, market sentiments, and potential impacts on the stock, along with the stock ticker."
        )

    def financial_analysis(self, agent): 
        return Task(
            description=dedent(f"""
                Conduct a thorough analysis of the stock's financial
                health and market performance. 
                This includes examining key financial metrics such as
                P/E ratio, EPS growth, revenue trends, and 
                debt-to-equity ratio. 
                Also, analyze the stock's performance in comparison 
                to its industry peers and overall market trends.

                Your final report MUST expand on the summary provided
                but now including a clear assessment of the stock's
                financial standing, its strengths and weaknesses, 
                and how it fares against its competitors in the current
                market scenario.
                
                {self.__tip_section()}

                Make sure to use the most recent data possible.
            """),
            agent=agent,
            expected_output="A detailed report on the stock's financial health, including analysis of key financial metrics and comparison with industry peers."
        )

    def filings_analysis(self, agent):
        return Task(
            description=dedent(f"""
                Analyze the latest 10-Q and 10-K filings from EDGAR for
                the stock in question. 
                Focus on key sections like Management's Discussion and
                Analysis, financial statements, insider trading activity, 
                and any disclosed risks.
                Extract relevant data and insights that could influence
                the stock's future performance.

                Your final answer must be an expanded report that now
                also highlights significant findings from these filings,
                including any red flags or positive indicators for
                your customer.
                
                {self.__tip_section()}        
            """),
            agent=agent,
            expected_output="A comprehensive report summarizing significant findings from 10-Q and 10-K filings, highlighting potential impacts on the stock's performance."
        )

    def recommend(self, agent):
        return Task(
            description=dedent(f"""
                Review and synthesize the analyses provided by the
                Financial Analyst and the Research Analyst.
                Combine these insights to form a comprehensive
                investment recommendation. 
                
                You MUST Consider all aspects, including financial
                health, market sentiment, and qualitative data from
                EDGAR filings.

                Make sure to include a section that shows insider 
                trading activity, and upcoming events like earnings.

                Your final answer MUST be a recommendation for your
                customer. It should be a full super detailed report, providing a 
                clear investment stance and strategy with supporting evidence.
                Make it pretty and well formatted for your customer.
                
                {self.__tip_section()}
            """),
            agent=agent,
            expected_output="A comprehensive investment recommendation report, including a detailed analysis and clear investment stance, well-formatted for the customer."
        )

    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"
    
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

        # Create message for ChatGPT analysis
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