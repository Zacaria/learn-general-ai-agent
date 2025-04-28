import os
from smolagents import LiteLLMModel

general_model = LiteLLMModel(
    model_id="openai/gpt-4.1-nano",
    api_base="https://api.openai.com/v1",
    api_key=os.environ["OPENAI_API_KEY"],
)