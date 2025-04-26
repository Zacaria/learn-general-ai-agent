class BasicAgent:
    def __init__(self):
        print("BasicAgent initialized.")

    def __call__(self, question: str) -> str:
        print(f"Agent received question (first 50 chars): {question[:50]}...")
        fixed_answer = f"This is my default answer for question: {question}"
        print(f"Agent returning fixed answer: {fixed_answer}")
        return fixed_answer
