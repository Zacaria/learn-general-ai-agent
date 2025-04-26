class BasicAgent:
    def __init__(self):
        print("BasicAgent initialized.")

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        fixed_answer = f"This is my default answer for question: {question}"
        print(f"Agent returning fixed answer: {fixed_answer}")
        return fixed_answer

def call_agent(agent, item):
    """
    Runs the agent on a single question item.
    Args:
        agent: An instantiated agent callable.
        item: dict with at least 'task_id' and 'question' keys.
    Returns:
        Tuple (result_log_dict, answer_payload_dict) or (None, None) if invalid.
    """
    task_id = item.get("task_id")
    question_text = item.get("question")
    if not task_id or question_text is None:
        print(f"Invalid question item: {item}")
        return None, None
    try:
        submitted_answer = agent(question_text)
        answer_payload = {"task_id": task_id, "submitted_answer": submitted_answer}
        result_log = {"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer}
        return result_log, answer_payload
    except Exception as e:
        print(f"Error running agent on task {task_id}: {e}")
        result_log = {"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"}
        return result_log, None