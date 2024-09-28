from crewai import Agent, Task
from textwrap import dedent
from langchain_openai import ChatOpenAI

gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o"
)

class EarningsSecAnalysisAgents:
    def financial_analyst(self):
        return Agent(
            llm=gpt_model,
            role='Financial Analyst',
            goal="Provide analysis based on SEC filings and earnings calls to guide investment decisions.",
            backstory="You are an expert financial analyst with deep knowledge of market trends and SEC regulations.",
            verbose=True
        )

    def analyze_sec_filings(self, agent, sec_data):
        return Task(
            description=dedent(f"""
                Analyze the SEC filings for potential risks, growth opportunities, and 
                financial trends. Focus on identifying patterns in the income statement,
                balance sheet, and cash flow.
                SEC Data: {sec_data}
            """),
            agent=agent,
            expected_output="A detailed analysis of SEC filings highlighting investment risks and opportunities."
        )

    def analyze_earnings_calls(self, agent, earnings_data):
        return Task(
            description=dedent(f"""
                Analyze the earnings calls for insights on the company's performance, market outlook, and 
                future guidance. Identify management's tone and sentiment.
                Earnings Data: {earnings_data}
            """),
            agent=agent,
            expected_output="A detailed earnings call analysis with insights into company performance and outlook."
        )
