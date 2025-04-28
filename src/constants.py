import os
import dotenv

dotenv.load_dotenv()

# (Keep Constants as is)
# --- Constants ---

DEFAULT_API_URL = "https://agents-course-unit4-scoring.hf.space"

questions_url = f"{DEFAULT_API_URL}/questions"
submit_url = f"{DEFAULT_API_URL}/submit"
space_id = os.getenv("SPACE_ID")

# In the case of an app running as a hugging Face space, this link points toward your codebase (usefull for others so please keep it public)
agent_code = f"https://huggingface.co/spaces/{space_id}/tree/main"

is_dry_run = os.environ.get("DRY_RUNNN", "").lower() == "true"