from src.question_fetcher import fetch_questions
from src.constants import questions_url

def get_question_choices():
    """
    Fetches questions and returns a tuple (choices, index_map).
    - choices: List of question strings for UI selection.
    - index_map: Dict mapping question string to its index in the original list.
    """
    err, questions_data = fetch_questions(questions_url)
    if err or not questions_data:
        return [], {}
    choices = [q.get("question", f"Question {i}") for i, q in enumerate(questions_data)]
    index_map = {q: i for i, q in enumerate(choices)}
    return choices, index_map
