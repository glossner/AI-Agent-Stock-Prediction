import langchain_openai as lang_oai




# LLM Models
gpt_4o_llm = lang_oai.ChatOpenAI(
    # The model name to use, like GPT-3.5 or GPT-4
    model_name="gpt-4o",  
    
    # Temperature controls the randomness of the output. 
    # Higher values (closer to 1.0) produce more random outputs, 
    # while lower values (0.0 to 0.5) make the output more deterministic.
    # Default: 0.7. 0.0 means deterministic
    temperature=0.0,  
    
    # Maximum number of tokens in the response. Controls the length of the output.
    max_tokens=100,  
    
    # Nucleus sampling. Only considers tokens with cumulative probability up to `top_p`.
    # value between 0.0 and 1.0 
    # Lower values make the model focus on more likely outputs.
    # Default: 0.9 (nucleus sampling).  
    #top_p=0.9,  
    
    # Number of responses to generate per prompt. Defaults to 1.
    #n=1,  
    
    # A list of strings or characters that indicate when the generation should stop.
    # Example: stop=["\n", "End of response"]
    # Default: None
    #stop=["\n"],  
    
    # Encourages the model to talk about new topics by penalizing repeated tokens. 
    # It ranges from -2.0 to 2.0. 
    # Positive values make the model less likely to repeat the same lines of thought.
    # Default: 0.0
    #presence_penalty=0.5,  
    
    # No penalty is applied for repeating tokens. 
    # By default, the model can repeat words or phrases without restriction (0.0)
    #frequency_penalty=0.0,  
    
    # This parameter would return token-level log probabilities if specified.
    # Default: None (no log probabilities)
    # Set to an integer value like 5 if you need log probabilities.
    #logprobs=None,  
    
    # Controls how many completions are generated and then chooses the "best" one.
    # Higher values increase the quality but use more tokens.
    # best_of=1,  
    
    # If True, returns results in real-time as they're generated.
    # The model will not stream responses by default. 
    # The response will be returned all at once after completion.  
    # streaming=False,  
    
    # Your OpenAI API key used for authentication.
    # api_key="your-openai-api-key",  
    
    # Custom API base URL, useful when working with proxies or custom setups.
    #openai_api_base="https://api.openai.com/v1",  
    
    # Allows specifying a timeout in seconds for requests to the OpenAI API.
    # request_timeout=30.0,  
    
    # The OpenAI organization to which the API key belongs. Optional.
    #openai_organization="your-organization-id",  
    
    # Specify a proxy server for routing API requests. Useful in restricted environments.
    #proxy="http://your-proxy-server:port"  
)