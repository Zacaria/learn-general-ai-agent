from smolagents import CodeAgent, Tool
from src.tools.general import visit_tool
from src.models import general_model

system_prompt = (
    f"You are a specialized agent. You must answer the user's question using ONLY the content of the given webpage."
    f"If the answer cannot be found or inferred from the webpage, respond with: 'EXCEPTION: The webpage does not allow answering the question.'"
    f"Before answering, you must control that the answer is coherent with the question."
    f"If the answer is not coherent with the question, respond with: 'EXCEPTION: The answer is not coherent with the question.'"
)

def format_prompt_for_webpage_agent(url: str, question: str) -> str:
    return f"{system_prompt}\nURL: {url}\nQuestion: {question}"

class UnderstandWebPageTool(Tool):
    name = "UnderstandWebPageTool"
    description = "This tool is responsible for answering the user's question using ONLY the content of the given webpage. If the answer cannot be found or inferred from the webpage, the tool will respond with an exception saying that the webpage does not allow answering the question."
    inputs = {
        "url": {
            "description": "The URL of the webpage to analyze in order to answer the user's question",
            "type": "string"
        },
        "question": {
            "description": "The user's question",
            "type": "string"
        }
    }
    output_type = "string"

    def __init__(self):
        self.agent = CodeAgent(
            model=general_model,
            tools=[visit_tool],
            add_base_tools=True,
            # max_steps=6,
            name="UnderstandWebPageAgent",
            description="This agent is responsible for answering the user's question using ONLY the content of the given webpage. If the answer cannot be found or inferred from the webpage, the agent will respond with an exception saying that the webpage does not allow answering the question.",
        )
        self.is_initialized = True
        print("UnderstandWebPageTool initialized.")

    def forward(self, url: str, question: str) -> str:
        prompt = format_prompt_for_webpage_agent(url, question)
        output = self.agent.run(prompt)
        # Check for explicit exception
        if "EXCEPTION:" in output:
            raise Exception("The webpage does not allow answering the question")
        answer = output
        if (
            answer.strip().lower().startswith("exception")
            or "does not allow" in answer.lower()
        ):
            raise Exception("The webpage does not allow answering the question")
        return str(answer)

understand_webpage_tool = UnderstandWebPageTool()