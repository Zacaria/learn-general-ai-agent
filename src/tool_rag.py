
from smolagents import CodeAgent, Tool
from src.tool_understand_web_page import understand_webpage_tool
from src.tools import search_tool, visit_tool
from src.models import general_model

systemPrompt = (
    f"You are a specialized agent in retrieveing information from webpages."
    f"You must reflect on the user's question and choose the best webpage to answer it."
    f"Start with more specialized webpages and then move to more general webpages like wikipedia."
    f"You will then iterate over the webpages until you find the answer."
    f"If the answer cannot be found or inferred from the web search, respond with: 'EXCEPTION: The websearch did not yield an answer.'"
    f"Before answering, you must control that the answer is coherent with the question."
    f"If the answer is not coherent with the question, respond with: 'EXCEPTION: The answer is not coherent with the question.'"
)

def format_prompt(question: str) -> str:
    return f"{systemPrompt}\n{question}"

class RAGTool(Tool):
    name = "RAGTool"
    description = "This tool is responsible for answering the user's question by using search and visit tools to retrieve information from webpages."
    inputs = {
        "question": {
            "description": "The user's question",
            "type": "string"
        }
    }
    output_type = "string"

    def __init__(self):
        self.agent = CodeAgent(
            model=general_model,
            tools=[search_tool, understand_webpage_tool],
            add_base_tools=True,
            max_steps=10,
            name="AgentRAG",
            description="This agent is responsible for answering the user's question by using search and visit tools to retrieve information from webpages."
        )
        self.is_initialized = True
        print("AgentRAG initialized.")
    
    def forward(self, question: str) -> str:
        prompt = format_prompt(question)
        output = self.agent.run(prompt)
        print(f"AgentRAG output: {output}")
        final_answer = output
        return str(final_answer)

rag_tool = RAGTool()