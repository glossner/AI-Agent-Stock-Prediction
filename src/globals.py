import os
import langchain_openai as oai
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Function to get API key
def get_openai_api_key():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    return api_key

# LLM Models
try:
    gpt_model = oai.ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.0,
        max_tokens=150,
        openai_api_key=get_openai_api_key()
    )
except Exception as e:
    print(f"Error initializing ChatOpenAI: {e}")
    gpt_model = None

# You can add other global variables or configurations here