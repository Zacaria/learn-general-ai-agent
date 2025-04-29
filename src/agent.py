
import os
import time
import traceback
import re
from smolagents import CodeAgent
from src.models import general_model
from src.tools.web_rag import web_rag_tool
from src.constants import files_url
from src.agent_understand_file import understand_file_agent

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
    f"You are a general AI assistant. I will ask you a QUESTION. Report your thoughts, and finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER]."
    "Some questions will have an optional file attached. If a file is attached, you should ALWAYS start by understanding what the file brings to the conversation, and then use it to answer the question."
    "To understand a file you should ALWAYS start by using your specialized agent in understanding files."
    "YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings."
    "If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise."
    "If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise."
    "If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string."
)

# def format_messages(question: str, file_url: str, file_type: str):
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": systemPrompt},
#                 {"type": "text", "text": question},
#                 {"type": "file_url", "file_url": file_url},
#                 {"type": "file_type", "file_type": file_type}
#             ],
#         }
#     ]
#     return messages

# def format_prompt_for_code_agent(question: str, file_path: str, file_type: str):
#     # if file_path:
#     #     return f"QUESTION:\n{question}\nFILE_PATH: {file_path}\nFILE_TYPE: {file_type}"
#     return f"QUESTION:\n{question}"

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
    return response

class ManagerAgent:
    def __init__(self):
        self.agent = CodeAgent(
            model=general_model,
            tools=[web_rag_tool],
            managed_agents=[understand_file_agent],
            add_base_tools=True,
            max_steps=10,
            name="ManagerAgent",
            planning_interval=3
        )
        self.agent.memory.system_prompt.system_prompt += f"\n{systemPrompt}"
        self.agent.visualize()

        print("ManagerAgent initialized.")

    def call(self, question: str) -> str:
        return self.call_with_file(question, None, None)
    
    def call_with_file(self, question: str, file_path: str, file_type: str) -> str:
        print(f"ManagerAgent received question (first 50 chars): {question[:50]}...")
        
        prompt= f"QUESTION:\n{question}"
        additional_args = None
        if file_path:
            additional_args = {
                "file_url": file_path,
                "file_type": file_type
            }
        output = self.agent.run(prompt, additional_args=additional_args)
        print(f"ManagerAgent output: {output}")
        return extract_final_answer(str(output))

def call_agent(agent, item):
    """
    Runs the agent on a single question item.
    Args:
        agent: An instantiated agent callable.
        item: dict with at least 'task_id' and 'question' keys.
    Returns:
        Tuple (result_log_dict, answer_payload_dict) or (None, None) if invalid.
    """
    start_time = time.time()
    
    task_id = item.get("task_id")
    question_text = item.get("question")
    file_name = item.get("file_name")
    if not task_id or question_text is None:
        print(f"Invalid question item: {item}")
        return None, None
    try:
        if file_name:
            name, file_type = os.path.splitext(file_name)
            file_path = f"{files_url}/{name}"
            submitted_answer = agent.call_with_file(question_text, file_path, file_type) 
        else:
            submitted_answer = agent.call(question_text)
        answer_payload = {"task_id": task_id, "submitted_answer": submitted_answer}
        result_log = {"Task ID": task_id, "Question": question_text, "Submitted Answer": submitted_answer}
        # Duration calculation
        end_time = time.time()
        duration = end_time - start_time
        if duration < 60:
            duration_str = f"{duration:.2f} seconds"
        else:
            mins = int(duration // 60)
            secs = duration % 60
            duration_str = f"{mins}m {secs:.2f}s"
        result_log["Duration"] = duration_str
        return result_log, answer_payload
    except Exception as e:
        print(f"Error running agent on task {task_id}: {e}")
        traceback.print_exc()
        result_log = {"Task ID": task_id, "Question": question_text, "Submitted Answer": f"AGENT ERROR: {e}"}
        return result_log, None