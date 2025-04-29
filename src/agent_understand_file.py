from smolagents import CodeAgent, Tool, FinalAnswerTool, PythonInterpreterTool, SpeechToTextTool
from src.models import general_model
from src.tools.audio_url_to_text import AudioUrlToTextTool

system_prompt = (
    f"You are a specialized agent in understanding files."
    f"You use the extension of the file to choose between suitable tools to interpret a provided file."
    f"You must help answering the user's question by returning the content of the file that is relevant to the question."
    f"You should only return the information gathered from the file and relevent to the question"
    # f"If the answer cannot be found or inferred from the file, respond with: 'EXCEPTION: The file does not allow answering the question.'"
    # f"Before answering, you must control that the answer is coherent with the question."
    # f"If the answer is not coherent with the question, respond with: 'EXCEPTION: The answer is not coherent with the question.'"
)

understand_file_agent = CodeAgent(
    model=general_model,
    tools=[FinalAnswerTool(), PythonInterpreterTool(), AudioUrlToTextTool()],
    add_base_tools=False,
    max_steps=10,
    name="UnderstandFileAgent",
    description=(
        f"This agent is responsible for understanding external files and returning the content of the file that is relevant to the question."
        f"This agent supports speech recognition, python file interpretation, and excel file processing."
        f"Always return a string as a return value."
    ),
    additional_authorized_imports=[
        'requests', 'pandas', 'openpyxl', 'io', 'os', 'urllib', 'pathlib'
    ]
)
understand_file_agent.memory.system_prompt.system_prompt += f"\n{system_prompt}"

# def format_prompt_for_file_agent(file_path: str, file_extension: str, question: str) -> str:
#     return f"FILE_PATH: {file_path}\nFILE_EXTENSION: {file_extension}\nQuestion: {question}"

# @tool
# def choose_tool_using_extension(file_extension: str) -> str:
#     """
#     Determines which tool or agent to use based on the file extension, in order to understand the file.

#     Args:
#         file_extension: extension of the file
#     Returns:
#         str: name of the tool or the agent to use
#     """
#     if file_extension == ".png":
#         return "vision_tool"
#     elif file_extension == ".mp3":
#         return "AudioUrlToTextTool"
#     elif file_extension == ".xlsx":
#         return "excel_tool"
#     elif file_extension == ".py":
#         return "PythonInterpreterTool"
#     else:
#         return "text_tool"

# class UnderstandFileTool(Tool):
#     name = "UnderstandFileTool"
#     description = "This tool is responsible for extending the comprehension of the user's question by returning the relevent information about the given file. The tool will use the question to identify the content of the file that is relevant to the question."
#     inputs = {
#         "file_path": {
#             "description": "The path to the file to be read.",
#             "type": "string"
#         },
#         "file_extension": {
#             "description": "The extension of the file.",
#             "type": "string"
#         },
#         "question": {
#             "description": "The user's question.",
#             "type": "string"
#         }
#     }
#     output_type = "string"
    
#     def __init__(self):
#         self.agent = understand_file_agent
#         self.is_initialized = True
#         print("UnderstandFileTool initialized.")
    
#     def forward(self, file_path: str, file_extension: str, question: str) -> str:
#         # prompt = format_prompt_for_file_agent(file_path, file_extension, question)
#         output = self.agent.run(question, additional_args={"file_path": file_path, "file_extension": file_extension})
#         # Check for explicit exception
#         # if "EXCEPTION:" in output:
#         #     raise Exception("The file does not allow answering the question")
#         # answer = output
#         # if (
#         #     answer.strip().lower().startswith("exception")
#         #     or "does not allow" in answer.lower()
#         # ):
#         #     raise Exception("The file does not allow answering the question")
#         return str(output)
        