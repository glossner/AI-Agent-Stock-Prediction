import logging
from textwrap import dedent
from pydantic import BaseModel, Field, ValidationError
import crewai as crewai
from src.Agents.base_agent import BaseAgent

# Initialize logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

class AskQuestionToCoworkerSchema(BaseModel):
    coworker: str = Field(..., description="The coworker to ask the question to.")
    question: str = Field(..., description="The question you want to ask.")
    context: str = Field(..., description="All necessary context for the coworker to understand the question.")

class ResearchAnalysisCriticAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            role='Research Analyst Critic Agent',
            goal="Critique the Research Analyst Agent's work",
            backstory='You have been trained for years to critique reports of research analysts agents',
            **kwargs
        )

        # Define the policy here
        self.policy = dedent("""
            **Policy:**

            - When using the 'Ask question to coworker' tool, you **must** include 'coworker', 'question', and 'context' in your **Action Input**.
            - The 'context' must contain all relevant information for the coworker to understand your question.
            - Do **not** omit any required fields.
            - If you fail to include all required fields, you will receive an error.
        """)

    def critique_research_analyst_agent(self):
        question = dedent("""
            Can you provide the complete content of your report, including details on SPY, DIA, and AGG?
        """).strip()

        context = dedent("""
            I am tasked with critiquing your report on recent market scenarios affecting SPY, DIA, and AGG. The current information only provides partial details about SPY. To provide a comprehensive critique, I need the full report, including all relevant data, analyses, and conclusions.
        """).strip()

        action_input = {
            "coworker": "scenario input agent",
            "question": question,
            "context": context
        }

        # Validate the action_input using Pydantic
        try:
            validated_input = AskQuestionToCoworkerSchema(**action_input)
            logger.debug(f"Validated Action Input: {validated_input.json()}")
        except ValidationError as e:
            logger.error(f"Validation Error: {e.json()}")
            raise e

        # Prepare the agent's system message, including the policy
        self.system_message = dedent(f"""
            As the Research Analyst Critic Agent, your goal is to critique the Research Analyst Agent's work.

            {self.policy}

            Remember, when using the 'Ask question to coworker' tool, ensure that you include the 'coworker', 'question', and 'context' fields in your **Action Input**. The 'context' should contain all the necessary information for the coworker to understand and answer your question.

            The coworkers know nothing about your question, so share absolutely everything you know. Do not reference things but instead explain them fully.
        """)

        # Return the task
        return crewai.Task(
            description=dedent("""
                Analyze the Research Analyst Agent's output. 
                Provide a detailed critique, highlighting specific areas for improvement, 
                and offer actionable suggestions to enhance the report.
            """),
            agent=self,
            expected_output="A critique of the Research Analyst Agent's report",
            action={
                "action": "Ask question to coworker",
                "action_input": validated_input.dict()
            }
        )