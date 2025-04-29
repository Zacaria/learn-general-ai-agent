import requests
import pandas as pd
from src.constants import submit_url, is_dry_run

def submit_answers(submission_data, results_log):
    """
    Submits answers to the specified URL and returns a tuple of (status_message, results_df).
    Args:
        submission_data (dict): The payload containing submission details.
        results_log (list): The log of results to be displayed in the DataFrame.
    Returns:
        Tuple[str, pd.DataFrame]: Status message and results DataFrame.
    """
    # Check if DRY_RUN environment variable is set to "true"
    if is_dry_run:
        return mock_submit_answers(submission_data, results_log)


    print(f"Submitting {len(submission_data['answers'])} answers to: {submit_url}")
    print(f"Submission payload: {submission_data}")
    try:
        response = requests.post(submit_url, json=submission_data, timeout=60)
        response.raise_for_status()
        result_data = response.json()
        final_status = (
            f"Submission Successful!\n"
            f"User: {result_data.get('username')}\n"
            f"Overall Score: {result_data.get('score', 'N/A')}% "
            f"({result_data.get('correct_count', '?')}/{result_data.get('total_attempted', '?')} correct)\n"
            f"Message: {result_data.get('message', 'No message received.')}"
        )
        print("Submission successful.")
        print(final_status)
        results_df = pd.DataFrame(results_log)
        return final_status, results_df
    except requests.exceptions.HTTPError as e:
        error_detail = f"Server responded with status {e.response.status_code}."
        try:
            error_json = e.response.json()
            error_detail += f" Detail: {error_json.get('detail', e.response.text)}"
        except requests.exceptions.JSONDecodeError:
            error_detail += f" Response: {e.response.text}"
        status_message = f"Submission Failed: {error_detail}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except requests.exceptions.RequestException as e:
        status_message = f"Submission Failed: Network error - {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df
    except Exception as e:
        status_message = f"An unexpected error occurred during submission: {e}"
        print(status_message)
        results_df = pd.DataFrame(results_log)
        return status_message, results_df

def mock_submit_answers(submission_data, results_log):
    """
    Mocks the submit_answers function for testing purposes.
    Args:
        submission_data (dict): The payload containing submission details.
        results_log (list): The log of results to be displayed in the DataFrame.
    Returns:
        Tuple[str, pd.DataFrame]: Status message and results DataFrame.
    """
    print(f"MOCK: Would submit {len(submission_data['answers'])} answers to: {submit_url}")
    
    # Create mock response data
    mock_result = {
        "username": "test_user",
        "score": 75.0,
        "correct_count": 3,
        "total_attempted": 4,
        "message": "This is a mock submission response."
    }
    
    final_status = (
        f"Mock Submission Successful!\n"
        f"User: {mock_result.get('username')}\n"
        f"Overall Score: {mock_result.get('score', 'N/A')}% "
        f"({mock_result.get('correct_count', '?')}/{mock_result.get('total_attempted', '?')} correct)\n"
        f"Message: {mock_result.get('message', 'No message received.')}"
    )
    
    print("Mock submission successful.")
    results_df = pd.DataFrame(results_log)
    return final_status, results_df
