from crewai import Task
from textwrap import dedent

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
      agent=agent
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
      agent=agent
    )

  def trend_detection(self, agent):
    return Task(
      description=dedent(f"""
        Analyze the stock's recent price action and technical indicators
        to detect the current market trend.
        Use moving averages, RSI, and MACD to support your analysis.

        Your final report MUST include:
        1. The identified trend (e.g., Strong Uptrend, Weak Downtrend, Sideways)
        2. Key technical levels (support and resistance)
        3. Any notable chart patterns or formations

        {self.__tip_section()}

        Ensure you're using the most up-to-date market data available.
      """),
      agent=agent
    )

  def trend_prediction(self, agent):
    return Task(
      description=dedent(f"""
        Based on historical data and current market conditions,
        predict how long the current trend is likely to continue.
        Use machine learning models or statistical methods for this prediction.

        Your final report MUST include:
        1. The estimated duration of the current trend in trading days
        2. The confidence level of your prediction
        3. Key factors that could potentially reverse the trend

        {self.__tip_section()}

        Make sure to use a robust methodology and explain your reasoning.
      """),
      agent=agent
    )

  def signal_generation(self, agent):
    return Task(
      description=dedent(f"""
        Based on the trend analysis and prediction, generate a clear
        buy, sell, or hold signal for the stock.
        Consider risk tolerance levels in your signal generation.

        Your final report MUST include:
        1. The generated signal (BUY, SELL, or HOLD)
        2. Suggested entry price (for BUY signals) or exit price (for SELL signals)
        3. Stop-loss and take-profit levels
        4. The reasoning behind the signal, including key risk factors

        {self.__tip_section()}

        Ensure your signal is actionable and includes proper risk management.
      """),
      agent=agent
    )

  def recommend(self, agent):
    return Task(
      description=dedent(f"""
        Review and synthesize all the analyses provided by the other agents.
        Combine these insights to form a comprehensive investment recommendation. 
        
        You MUST consider all aspects, including financial health, market sentiment,
        technical analysis, trend predictions, and the generated trading signal.

        Your final answer MUST be a recommendation for your customer. 
        It should be a full, super detailed report, providing a 
        clear investment stance and strategy with supporting evidence.
        Make it pretty and well formatted for your customer.
        
        Include:
        1. Overall recommendation (Strong Buy, Buy, Hold, Sell, Strong Sell)
        2. Summary of all analyses (fundamental, technical, sentiment)
        3. Potential catalysts and risk factors
        4. Suggested position size and risk management strategy
        5. Timeline for the investment (short-term, medium-term, long-term)

        {self.__tip_section()}
      """),
      agent=agent
    )

  def __tip_section(self):
    return "If you do your BEST WORK, I'll give you a $10,000 commission!"