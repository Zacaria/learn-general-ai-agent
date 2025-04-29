import os
import requests
from urllib.parse import urlparse
from litellm import transcription
# from transformers import pipeline
from smolagents import Tool, SpeechToTextTool, LiteLLMModel
from pathlib import Path

# model = LiteLLMModel(model_id="openai/whisper-large-v3-turbo", api_key=os.environ["OPENAI_API_KEY"])

def audio_to_text(audio_file_path: os.PathLike) -> str:
    try:
        print(f"Processing audio file: {audio_file_path}")

        output = transcription(model="openai/gpt-4o-mini-transcribe", file=audio_file_path, api_key=os.environ["OPENAI_API_KEY"])
        return output
        # asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3-turbo", model_kwargs={"api_key": os.environ["OPENAI_API_KEY"]})
        # result = asr(audio_file_path)
        # print("Transcription result: ", result)
        # return result["text"]
    except Exception as e:
        return f"Error: {str(e)}"

class AudioUrlToTextTool(Tool):
    name = "AudioUrlToTextTool"
    description = "Reads an audio file from the given url and returns the transcribed text."
    inputs = {
        "audio_url": {
            "description": "URL to the audio file.",
            "type": "string"
        },
        "file_extension": {
            "description": "extension of the file including the dot",
            "type": "string"
        }
    }
    output_type = "string"
    
    def forward(self, audio_url: str, file_extension: str) -> str:
        try:
            os.makedirs("./data", exist_ok=True)
            file_name = os.path.basename(urlparse(audio_url).path) or "audio_file"
            file_path = Path(os.path.join("./data", file_name + file_extension))
            # Download file
            try:
                response = requests.get(audio_url, timeout=30)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            except Exception as download_err:
                print(f"Download failed: {download_err}. Trying fallback if file exists.")
                if not os.path.exists(file_path):
                    return f"Error: Could not download or find fallback file. {download_err}"
            # Run pipeline
            try:
                return audio_to_text(file_path)
            except Exception as pipeline_err:
                print(f"Pipeline failed: {pipeline_err}. Trying fallback if file exists.")
                if os.path.exists(file_path):
                    return audio_to_text(file_path)
                return f"Error: Could not process audio. {pipeline_err}"
        except Exception as e:
            return f"Error: {str(e)}"
