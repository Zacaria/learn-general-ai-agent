import os
from smolagents import CodeAgent, Tool
from src.models import general_model
from urllib.parse import urlparse
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

system_prompt = (
    f"You are a specialized agent in interpreting images."
    f"You must help answering the user's question by returning the content of the image that is relevant to the question."
    f"Double check that you have not missed any details in the image."
    # f"You should only return the information gathered from the image and relevent to the question"
)

vision_agent = CodeAgent(
    model=general_model,
    tools=[],
    add_base_tools=True,
    # max_steps=10,
    name="VisionAgent",
    description=(
        f"This agent is responsible for understanding images and returning the content of the image that is relevant to the question."
        f"Always return a string as a return value."
    )
)

vision_agent.memory.system_prompt.system_prompt += f"\n{system_prompt}"

class VisionTool(Tool):
    name = "VisionTool"
    description = "Reads an image file from the given url and returns the content of the image that is relevant to the question."
    inputs = {
        "prompt": {
            "description": "The user's question.",
            "type": "string"
        },
        "image_url": {
            "description": "URL to the image file.",
            "type": "string"
        },
        "file_extension": {
            "description": "extension of the file including the dot",
            "type": "string"
        }
    }
    output_type = "string"
    
    def __init__(self):
        self.agent = vision_agent

        self.is_initialized = True
    
    def forward(self, prompt: str, image_url: str, file_extension: str) -> str:
        try:
            os.makedirs("./data", exist_ok=True)
            file_name = os.path.basename(urlparse(image_url).path) or "image_file"
            file_path = Path(os.path.join("./data", file_name + file_extension))
            # Download file
            try:
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            except Exception as download_err:
                print(f"Download failed: {download_err}. Trying fallback if file exists.")
                if not os.path.exists(file_path):
                    return f"Error: Could not download or find fallback file. {download_err}"

            try:
                image = Image.open(BytesIO(response.content)).convert("RGB")
                images = [image]
                return self.agent.run(prompt, images=images)
            except Exception as pipeline_err:
                print(f"Pipeline failed: {pipeline_err}. Trying fallback if file exists.")
                if os.path.exists(file_path):
                    return self.agent.run(file_path)
                return f"Error: Could not process audio. {pipeline_err}"
        except Exception as e:
            return f"Error: {str(e)}"
        