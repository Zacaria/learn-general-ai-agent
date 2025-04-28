from dotenv import load_dotenv
import os
from src.submit_questions import submit_answers
import pandas as pd
import gradio as gr
from src.question_choices import get_question_choices
from src.question_fetcher import fetch_questions
from src.agent import ManagerAgent, call_agent
from src.constants import agent_code, is_dry_run

load_dotenv()

def run_and_submit_all(profile: gr.OAuthProfile | None):
    """
    Fetches all questions, runs the ManagerAgent on them, submits all answers,
    and displays the results.
    """
    # --- Determine HF Space Runtime URL and Repo URL ---
    if profile:
        username= f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    # 1. Instantiate Agent ( modify this part to create your agent)
    try:
        agent = ManagerAgent()
    except Exception as e:
        print(f"Error instantiating agent: {e}")
        return f"Error initializing agent: {e}", None
    
    print(agent_code)

    # 2. Fetch Questions
    err, questions_data = fetch_questions()
    if err:
        return err, None
    # 3. Run your Agent
    results_log = []
    answers_payload = []
    print(f"Running agent on {len(questions_data)} questions...")
    for item in questions_data:
        result_log, answer_payload = call_agent(agent, item)
        if result_log is not None and answer_payload is not None:
            results_log.append(result_log)
            answers_payload.append(answer_payload)

    if not answers_payload:
        print("Agent did not produce any answers to submit.")
        return "Agent did not produce any answers to submit.", pd.DataFrame(results_log)

    # 4. Prepare Submission 
    submission_data = {"username": username.strip(), "agent_code": agent_code, "answers": answers_payload}
    status_update = f"Agent finished. Submitting {len(answers_payload)} answers for user '{username}'..."
    print(status_update)

    # 5. Submit
    return submit_answers(submission_data, results_log)

def run_one_and_submit(profile: gr.OAuthProfile | None, selected_q: str):
    """
    Fetches questions, runs the ManagerAgent on a specific question, submits the answer,
    and displays the result.
    
    Args:
        profile: The user's OAuth profile
        selected_q: The question string to run
    
    Returns:
        Tuple of (status message, results dataframe)
    """
    # --- Determine HF Space Runtime URL and Repo URL ---
    if profile:
        username = f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    # 1. Instantiate Agent
    try:
        agent = ManagerAgent()
    except Exception as e:
        print(f"Error instantiating agent: {e}")
        return f"Error initializing agent: {e}", None
    
    print(agent_code)

    # 2. Fetch Questions
    err, questions_data = fetch_questions()
    if err:
        return err, None

    _, question_index_map = get_question_choices()
    question_index = question_index_map.get(selected_q, 0)
    
    # Check if question_index is valid
    if question_index < 0 or question_index >= len(questions_data):
        return f"Invalid question index: {question_index}. Must be between 0 and {len(questions_data)-1}.", None
    
    # 3. Run Agent on specific question
    results_log = []
    answers_payload = []
    
    item = questions_data[question_index]
    result_log, answer_payload = call_agent(agent, item)
    if result_log is None or answer_payload is None:
        return "Invalid question item with missing task_id or question.", None
    results_log.append(result_log)
    answers_payload.append(answer_payload)

    # 4. Prepare Submission 
    submission_data = {"username": username.strip(), "agent_code": agent_code, "answers": answers_payload}
    status_update = f"Agent finished. Submitting answer for question {question_index} for user '{username}'..."
    print(status_update)

    # 5. Submit
    return submit_answers(submission_data, results_log)


# --- Build Gradio Interface using Blocks ---
with gr.Blocks() as demo:
    gr.Markdown("# Basic Agent Evaluation Runner")
    gr.Markdown(
        """
        **Instructions:**

        1.  Please clone this space, then modify the code to define your agent's logic, the tools, the necessary packages, etc ...
        2.  Log in to your Hugging Face account using the button below. This uses your HF username for submission.
        3.  Click 'Run Evaluation & Submit All Answers' to fetch questions, run your agent, submit answers, and see the score.

        ---
        **Disclaimers:**
        Once clicking on the "submit button, it can take quite some time ( this is the time for the agent to go through all the questions).
        This space provides a basic setup and is intentionally sub-optimal to encourage you to develop your own, more robust solution. For instance for the delay process of the submit button, a solution could be to cache the answers and submit in a seperate action or even to answer the questions in async.
        """
    )

    gr.LoginButton()

    # --- Run a Single Question ---
    gr.Markdown("# Run one question")
    question_choices, question_index_map = get_question_choices()

    question_dropdown = gr.Dropdown(
        choices=question_choices,
        label="Select a Question",
        interactive=True
    )

    run_single_button = gr.Button("Run Single Question")

    single_status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
    single_results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

    run_single_button.click(
        fn=run_one_and_submit,
        inputs=[question_dropdown],
        outputs=[single_status_output, single_results_table]
    )

    # --- Run All Questions ---
    gr.Markdown("# Run all questions")
    run_button = gr.Button("Run Evaluation & Submit All Answers")

    status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
    # Removed max_rows=10 from DataFrame constructor
    results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

    run_button.click(
        fn=run_and_submit_all,
        outputs=[status_output, results_table]
    )

if __name__ == "__main__":
    print("\n" + "-"*30 + " App Starting " + "-"*30)
    # Check for SPACE_HOST and SPACE_ID at startup for information
    space_host_startup = os.getenv("SPACE_HOST")
    space_id_startup = os.getenv("SPACE_ID") # Get SPACE_ID at startup

    # Check and display DRY_RUN status
    if is_dry_run:
        print("🧪 DRY_RUN mode is active. Submissions will be mocked.")
    else:
        print("🚀 Live submission mode is active.")


    if space_host_startup:
        print(f"✅ SPACE_HOST found: {space_host_startup}")
        print(f"   Runtime URL should be: https://{space_host_startup}.hf.space")
    else:
        print("ℹ️  SPACE_HOST environment variable not found (running locally?).")

    if space_id_startup: # Print repo URLs if SPACE_ID is found
        print(f"✅ SPACE_ID found: {space_id_startup}")
        print(f"   Repo URL: https://huggingface.co/spaces/{space_id_startup}")
        print(f"   Repo Tree URL: https://huggingface.co/spaces/{space_id_startup}/tree/main")
    else:
        print("ℹ️  SPACE_ID environment variable not found (running locally?). Repo URL cannot be determined.")

    print("-"*(60 + len(" App Starting ")) + "\n")

    print("Launching Gradio Interface for Basic Agent Evaluation...")
    demo.launch(debug=True, share=False)