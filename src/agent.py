
import re
from smolagents import CodeAgent
from src.models import general_model
from src.tool_rag import rag_tool

# Original GAIA system prompt

# systemPromptGAIA = (
#     f"You are a general AI assistant."
#     "I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]."
#     "YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings."
#     "If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise."
#     "If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise."
#     "If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."
# )

# Custom system prompt
systemPrompt = (
    f"You are a general AI assistant. I will ask you a question. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]."
    "YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings."
    "If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise."
    "If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise."
    "If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."
)

def format_messages(question: str):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": systemPrompt},
                {"type": "text", "text": question},
            ],
        }
    ]
    return messages

def format_prompt_for_code_agent(question: str):
    return f"{systemPrompt}\n{question}"

def extract_final_answer(response: str) -> str:
    # Define patterns to look for final answer with case insensitivity
    patterns = [
        r"FINAL ANSWER:\s*\[?([^\]\n]+)\]?",
        r"FINAL ANSWER:\s*([^\n]+)",
        r"ANSWER:\s*\[?([^\]\n]+)\]?"
    ]
    
    # Try each pattern until we find a match
    match = None
    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            break
    if match:
        return match.group(1)
    # Ensure final answer is returned as a string
    if response is None:
        return ""
    return str(response)

class ManagerAgent:
    def __init__(self):
        self.agent = CodeAgent(
            model=general_model,
            tools=[rag_tool],
            add_base_tools=True,
            max_steps=10,
            name="ManagerAgent"
        )
        self.agent.visualize()

        print("ManagerAgent initialized.")
    
    def __call__(self, question: str) -> str:
        print(f"ManagerAgent received question (first 50 chars): {question[:50]}...")
        
        messages = format_prompt_for_code_agent(question)
        output = self.agent.run(messages)
        print(f"ManagerAgent output: {output}")
        final_answer = extract_final_answer(output)
        return final_answer
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