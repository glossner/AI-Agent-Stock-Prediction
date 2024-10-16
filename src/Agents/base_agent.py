import os
from openai import OpenAI
from pydantic import BaseModel, Field , ConfigDict
from typing import Optional, Any
import pandas as pd

class BaseAgent(BaseModel):
    role: str = Field(..., description="The role of the agent in the stock analysis system")
    goal: str = Field(..., description="The primary goal or objective of the agent")
    backstory: str = Field(..., description="Background information about the agent")
    model: Optional[Any] = Field(None, description="The underlying model used by the agent, if applicable")

    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    client: Optional[OpenAI] = Field(default=None, description="OpenAI client")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and self.client is None:
            self.client = OpenAI(api_key=self.api_key)

    def call_model(self, prompt: str) -> str:
        if self.client is None:
            raise ValueError("OpenAI client is not initialized. Make sure API key is set.")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analysis assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            return None

    def construct_message(self, data: pd.DataFrame) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    def analyze(self, data: pd.DataFrame) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")

    def respond(self, data: pd.DataFrame) -> str:
        raise NotImplementedError("Subclasses should implement this method.")