
from smolagents import CodeAgent, Tool
from src.tools.understand_web_page import understand_webpage_tool
from src.tools.general import search_tool
from src.models import general_model

systemPrompt = (
    f"You are a specialized agent in retrieveing information from webpages."
    f"You must reflect on the user's question and choose the best webpage to answer it."
    f"Start with more specialized webpages and then move to more general webpages like wikipedia."
    f"However, if wikipedia is explicitly requested, use your Wikipedia search tool straight away."
    f"You will then iterate over the webpages until you find the answer."
    f"If the answer cannot be found or inferred from the web search, respond with: 'EXCEPTION: The websearch did not yield an answer.'"
    f"Before answering, you must control that the answer is coherent with the question."
    f"If the answer is not coherent with the question, respond with: 'EXCEPTION: The answer is not coherent with the question.'"
)

web_rag_agent = CodeAgent(
    model=general_model,
    tools=[search_tool, understand_webpage_tool],
    add_base_tools=True,
    # max_steps=10,
    name="WebSearchAgent",
    description="This agent is responsible for answering the user's question by using search and visit tools to retrieve information from webpages."
)

web_rag_agent.memory.system_prompt.system_prompt += f"\n{systemPrompt}"

# class RAGTool(Tool):
#     name = "RAGTool"
#     description = "This tool is responsible for answering the user's question by using search and visit tools to retrieve information from webpages."
#     inputs = {
#         "question": {
#             "description": "The user's question",
#             "type": "string"
#         }
#     }
#     output_type = "string"

#     def __init__(self):
#         self.agent = web_rag_agent
#         self.is_initialized = True
#         print("WebSearchAgent initialized.")
    
#     def forward(self, question: str) -> str:
#         output = self.agent.run(question)
#         final_answer = output
#         return str(final_answer)

# web_rag_tool = RAGTool()