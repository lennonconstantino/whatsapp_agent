import colorama
from typing import Dict, Any, List
from colorama import Fore
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app.infrastructure.llm import LLM, models
from app.domain.tools.base import Tool, ToolResult

class StepResult(BaseModel):
    event: str
    content: str
    success: bool

SYSTEM_MESSAGE = """You are tasked with completing specific objectives and must report the outcomes. At your disposal, you have a variety of tools, each specialized in performing a distinct type of task.

For successful task completion:
Thought: Consider the task at hand and determine which tool is best suited based on its capabilities and the nature of the work. If you can complete the task or answer a question, soley by the information provided you can use the report_tool directly.

Use the report_tool with an instruction detailing the results of your work or to answer a user question.
If you encounter an issue and cannot complete the task:

Use the report_tool to communicate the challenge or reason for the task's incompletion.
You will receive feedback based on the outcomes of each tool's task execution or explanations for any tasks that couldn't be completed. This feedback loop is crucial for addressing and resolving any issues by strategically deploying the available tools.

Return only one tool call at a time.

# Context Information for this task:
{context}
"""

class Agent:

    def __init__(
            self,
            tools: List[Tool],
            system_message: str = SYSTEM_MESSAGE,
            llm: Dict[str, Any] = models,
            max_steps: int = 5,
            verbose: bool = True,
            examples: List[dict] = None,
            context: str = None,
            user_context: str = None
    ):
        self.tools = tools
        self.llm = llm
        self.system_message = system_message
        self.memory = []
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.examples = examples or []
        self.context = context or ""
        self.user_context = user_context

    def to_console(self, tag: str, message: str, color: str = "green"):
        if self.verbose:
            color_prefix = Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")

    def run(self, user_input: str, context: str = None):
        # Converter tools para formato LangChain
        langchain_tools = [tool.langchain_tool_schema for tool in self.tools]
        system_message = self.system_message.format(context=context)

        if self.user_context:
            context = context if context else self.user_context

        if context:
            user_input = f"{context}\n---\n\nUser Message: {user_input}"

        self.to_console("START", f"Starting Agent with Input:\n'''{user_input}'''")

        self.step_history = [
            {"role": "system", "content": system_message},
            *self.examples,
            {"role": "user", "content": user_input}
        ]

        step_result = None
        i = 0

        while i < self.max_steps:
            step_result = self.run_step(self.step_history, langchain_tools)
            if step_result.event == "finish":
                break
            elif step_result.event == "error":
                self.to_console(step_result.event, step_result.content, "red")
            else:
                self.to_console(step_result.event, step_result.content, "yellow")

            i += 1

        self.to_console("Final Result", step_result.content, "green")
        return step_result.content

    def run_step(self, messages: List[dict], tools):
        # Converter mensagens para formato LangChain
        langchain_messages = self._convert_to_langchain_messages(messages)

        # Bind tools e invocar
        model = self.llm[LLM]
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(langchain_messages)

        # Verificar múltiplas tool calls
        if response.tool_calls and len(response.tool_calls) > 1:
            messages = [
                *self.step_history,
                {"role": "user", "content": "Error: Please return only one tool call at a time."}
            ]
            return self.run_step(messages, tools)

        # Adicionar mensagem do assistente ao histórico
        assistant_message = {
            "role": "assistant", 
            "content": response.content,
            "tool_calls": response.tool_calls if response.tool_calls else None
        }
        self.step_history.append(assistant_message)
        
        # Verificar se há tool call
        if not response.tool_calls:
            msg = response.content
            step_result = StepResult(
                event="Error", 
                content=f"No tool calls were returned.\nMessage: {msg}", 
                success=False
            )
            return step_result

        # Extrair informações da tool
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Executar a tool
        self.to_console("Tool Call", f"Name: {tool_name}\nArgs: {tool_args}\nMessage: {response.content}", "magenta")
        tool_result = self._run_tool_langchain(tool_call, self.tools)
        tool_result_msg = self.tool_call_message_langchain(tool_call, tool_result)
        self.step_history.append(tool_result_msg)

        # Verificar se é report_tool para finalizar
        if tool_name == "report_tool":
            step_result = StepResult(
                event="finish",
                content=tool_result.content,
                success=True
            )
            return step_result

        # Processar resultado da tool
        if tool_result.success:
            step_result = StepResult(
                event="tool_result",
                content=tool_result.content,
                success=True
            )
        else:
            step_result = StepResult(
                event="error",
                content=tool_result.content,
                success=False
            )

        return step_result

    def _run_tool_langchain(self, tool_call: dict, tools: List[Tool]) -> ToolResult:
        """Executa uma tool call no formato LangChain."""
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Encontrar a tool
        tool = None
        for t in tools:
            if t.name == tool_name:
                tool = t
                break
        
        if not tool:
            return ToolResult(
                content=f"Tool '{tool_name}' not found",
                success=False
            )
        
        try:
            return tool._run(**tool_args)
        except Exception as e:
            return ToolResult(
                content=f"Error running tool '{tool_name}': {str(e)}",
                success=False
            )

    def tool_call_message_langchain(self, tool_call: dict, tool_result: ToolResult):
        """Cria mensagem de resposta da tool para LangChain."""
        return {
            "tool_call_id": tool_call.get("id", "unknown"),
            "role": "tool",
            "name": tool_call["name"],
            "content": tool_result.content,
        }

    def _convert_to_langchain_messages(self, messages: List[dict]):
        """Converte mensagens do formato OpenAI para LangChain."""
        langchain_messages = []
        
        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                # Para mensagens de assistant, verificar se têm tool_calls
                if msg.get("tool_calls"):
                    # Se tem tool_calls, criar AIMessage com tool_calls
                    langchain_messages.append(AIMessage(
                        content=msg["content"],
                        tool_calls=msg["tool_calls"]
                    ))
                    
                    # Verificar se há mensagens de tool correspondentes
                    tool_call_ids = [tc.get("id") for tc in msg["tool_calls"]]
                    for j in range(i + 1, len(messages)):
                        next_msg = messages[j]
                        if (next_msg["role"] == "tool" and 
                            next_msg.get("tool_call_id") in tool_call_ids):
                            # Incluir mensagem de tool que responde a este tool_call
                            langchain_messages.append(ToolMessage(
                                content=next_msg["content"],
                                tool_call_id=next_msg["tool_call_id"]
                            ))
                else:
                    # Mensagem normal de assistant
                    langchain_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "tool":
                # Só incluir mensagens de tool se não foram incluídas acima
                # (elas são incluídas quando processamos mensagens de assistant com tool_calls)
                pass
        
        return langchain_messages