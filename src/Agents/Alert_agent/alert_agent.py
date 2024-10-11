from crewai import Agent
from langchain_openai import ChatOpenAI

gpt_model = ChatOpenAI(
    temperature=0,
    model_name="gpt-4o"
)

class AlertAgent:
    def __init__(self):
        self.agent = Agent(
            llm=gpt_model,
            role='Stock Alert Analyst',
            goal="Monitor stock prices and trends to trigger alerts.",
            backstory="A highly experienced analyst monitoring market trends to send near real-time alerts.",
            verbose=True
        )
    
    def analyze_stock_changes(self, stock_data):
        return self.agent.run(f"Analyze the stock changes: {stock_data}")
