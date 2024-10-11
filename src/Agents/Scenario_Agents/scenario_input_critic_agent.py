import re
from pydantic import BaseModel, Field
from textwrap import dedent
import crewai as crewai
from src.Agents.base_agent import BaseAgent

class AskQuestionToCoworkerSchema(BaseModel):
    coworker: str = Field(..., description="The coworker to ask the question to.")
    question: str = Field(..., description="The question you want to ask.")
    context: str = Field(..., description="All necessary context for the coworker to understand the question.")

class ScenarioInputCriticAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role='Scenario Input Critic Agent',
            goal="Critique the Scenario Input Agent's work",
            backstory='You have been trained for years to critique reports of financial agents',
            **kwargs
        )

    def critique_scenario_input_agent(self):
        action_input = {
            "coworker": "Scenario Input Agent",
            "question": "Can you provide the complete report on recent market scenarios affecting SPY, DIA, and AGG? The current context is incomplete, and I need the full report to perform a comprehensive critique.",
            "context": (
                "I am critiquing the Scenario Input Agent's report on recent market scenarios affecting SPY, DIA, and AGG. "
                "However, the information I currently have is incomplete. To provide a thorough and accurate critique, "
                "I need access to the complete report, including all data, analyses, and insights related to these market scenarios."
            )
        }

        return crewai.Task(
            description=dedent("""
                Analyze the Scenario Input Agent's output. Critique it and if appropriate
                direct the Scenario Agent to write a better report.
            """),
            agent=self,
            expected_output="A critique of the Scenario Input Agent's report",
            action={
                "action": "Ask question to coworker",
                "action_input": action_input
            }
        )
