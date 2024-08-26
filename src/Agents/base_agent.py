from openai import OpenAI
import os
import json
import pandas as pd


# model="gpt-4o"
class BaseAgent:
    def __init__(self, model="gpt-3.5"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.model = model

    def call_model(self, data_list, **kwargs):
        client = OpenAI(api_key=self.api_key)
        prompt = self.construct_message(data_list, **kwargs)

        try:
            # Make the API call using the latest interface
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analysis assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Print the raw response for debugging
            print("Raw API response:", response)

            # Ensure the response has the expected structure
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print("Raw content:", content)  # Print the raw content
                return json.loads(content)
            else:
                raise ValueError("Invalid response format: no choices found.")

        except Exception as e:
            # Handle and log the exception
            print(f"Error during API call: {e}")
            return None

    def construct_message(self, data_list, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")
