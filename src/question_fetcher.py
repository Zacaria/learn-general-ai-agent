import requests
import os
import json
from src.constants import questions_url

def fetch_questions():
    """
    Fetch questions from the remote endpoint, with fallback to local questions.json if 429 is received.
    Returns a tuple: (error_message_or_None, questions_data_or_None)
    """

    print(f"Fetching questions from: {questions_url}")
    try:
        response = requests.get(questions_url, timeout=15)
        response.raise_for_status()
        questions_data = response.json()
        if not questions_data:
            print("Fetched questions list is empty.")
            return "Fetched questions list is empty or invalid format.", None
        print(f"Fetched {len(questions_data)} questions.")
        return None, questions_data
    except requests.exceptions.RequestException as e:
        # Fallback to local file if 429 Too Many Requests
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
            print("Received 429 Too Many Requests. Falling back to local questions.json file.")
            local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'questions.json')
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    questions_data = json.load(f)
                if not questions_data:
                    print("Local questions.json is empty or invalid format.")
                    return "Local questions.json is empty or invalid format.", None
                print(f"Loaded {len(questions_data)} questions from local file.")
                return None, questions_data
            except Exception as file_e:
                print(f"Error loading local questions.json: {file_e}")
                return f"Error loading local questions.json: {file_e}", None
        print(f"Error fetching questions: {e}")
        return f"Error fetching questions: {e}", None
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error decoding JSON response from questions endpoint: {e}")
        print(f"Response text: {response.text[:500]}")
        return f"Error decoding server response for questions: {e}", None
    except Exception as e:
        print(f"An unexpected error occurred fetching questions: {e}")
        return f"An unexpected error occurred fetching questions: {e}", None
