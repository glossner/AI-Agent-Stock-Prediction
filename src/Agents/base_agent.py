from openai import OpenAI
import os
import json
import pandas as pd
import src.globals as globals
import crewai as crewai
from pydantic import ConfigDict
import logging


class BaseAgent(crewai.Agent):
    model_config = ConfigDict(extra='allow',arbitrary_types_allowed=True)

    def __init__(self, **kwargs):
        # require role, goal, and backstory to be initialized
        role = kwargs.pop('role', None)
        goal = kwargs.pop('goal', None)
        backstory = kwargs.pop('backstory', None)

        if role is None:
            raise ValueError("The 'role' parameter must be provided.")
        if goal is None:
            raise ValueError("The 'goal' parameter must be provided.")
        if backstory is None:
            raise ValueError("The 'backstory' parameter must be provided.")       

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            #tools=kwargs.get('tools', []),   #[my_tool1, my_tool2],  # Optional, defaults to an empty list
            llm=kwargs.pop('llm', globals.gpt_4o_llm),
            #function_calling_llm=my_llm,  # Optional
            max_iter=kwargs.pop('max_iter', 15),  # Optional
            max_rpm=kwargs.pop('max_rpm', 60*4), # Optional
            max_execution_time=kwargs.pop('max_execution_time', None), # Optional
            verbose=kwargs.pop('verbose', True),  # Optional
            allow_delegation=kwargs.pop('allow_delegation', True),  # Optional
            #step_callback=my_intermediate_step_callback,  # Optional
            cache=kwargs.pop('cache', True),  # Optional
            #system_template=my_system_template,  # Optional
            #prompt_template=my_prompt_template,  # Optional
            #response_template=my_response_template,  # Optional
            #config=my_config,  # Optional
            #crew=my_crew,  # Optional
            #tools_handler=my_tools_handler,  # Optional
            #cache_handler=my_cache_handler,  # Optional
            #callbacks=[callback1, callback2],  # Optional
            allow_code_execution=kwargs.pop('allow_code_execution', False),  # Optiona
            max_retry_limit=kwargs.pop('max_retry_limit', 2),  # Optional
            **kwargs
        )

      # Initialize the logger
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            # Set up logging format and level if not already configured
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            

# model="gpt-4o"
# class BaseAgent:
#     def __init__(self, model="gpt-3.5"):
#         self.api_key = os.getenv("OPENAI_API_KEY")
#         if not self.api_key:
#             raise ValueError("OPENAI_API_KEY environment variable is not set")
#         self.model = model

#     def call_model(self, data_list, **kwargs):
#         client = OpenAI(api_key=self.api_key)
#         prompt = self.construct_message(data_list, **kwargs)

#         try:
#             # Make the API call using the latest interface
#             response = client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system", "content": "You are a financial analysis assistant."},
#                     {"role": "user", "content": prompt}
#                 ]
#             )

#             # Print the raw response for debugging
#             print("Raw API response:", response)

#             # Ensure the response has the expected structure
#             if response.choices and len(response.choices) > 0:
#                 content = response.choices[0].message.content
#                 print("Raw content:", content)  # Print the raw content
#                 return json.loads(content)
#             else:
#                 raise ValueError("Invalid response format: no choices found.")

#         except Exception as e:
#             # Handle and log the exception
#             print(f"Error during API call: {e}")
#             return None

#     def construct_message(self, data_list, **kwargs):
#         raise NotImplementedError("Subclasses should implement this method.")
