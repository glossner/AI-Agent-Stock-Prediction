import openai
import os
import json
import pandas as pd

class IndicatorAgent:
    def __init__(self, model="gpt-4"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = self.api_key
        self.model = model

    def call_model(self, data_list, **kwargs):
        prompt = self.construct_message(data_list, **kwargs)

        # Make the API call using the latest interface
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return json.loads(response['choices'][0]['message']['content'])

    def construct_message(self, data_list, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")
