import uuid
import colorama
from typing import Dict, Any, List
from colorama import Fore
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app.domain.agents.utils import parse_function_args, run_tool_from_response
from app.infrastructure.llm import LLM, models
from app.domain.tools.tool import Tool, ToolResult

class StepResult(BaseModel):
    event: str
    content: str
    success: bool

SYSTEM_MESSAGE = """# Task Execution Agent

You are a task execution agent that MUST use tools to complete tasks and ALWAYS finish with report_tool.

## CRITICAL RULES:
1. **ALWAYS use tools** - Never respond without calling a tool
2. **ALWAYS end with report_tool** - Every task must conclude with report_tool
3. **Use one tool at a time** - Execute tools sequentially
4. **Complete the task** - Don't stop until you've used report_tool

## Available Tools:
- **query_data_tool**: For database queries
- **add_expense_tool**: For adding expenses  
- **add_revenue_tool**: For adding revenue
- **add_customer_tool**: For adding customers
- **report_tool**: For final reporting (MANDATORY)

## Simple Workflow:
1. **Analyze** the user's request
2. **Choose** the appropriate tool
3. **Execute** the tool with correct parameters
4. **Use report_tool** to provide the final answer

## Example:
User: "What are my expenses?"
Action: Use query_data_tool → Get results → Use report_tool with summary

## Remember:
- You MUST use tools
- You MUST use report_tool at the end
- Keep responses focused and direct
- Always explain what you're doing before using tools

{context}"""

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
                event="error", 
                content=f"No tool calls were returned.\nMessage: {msg}", 
                success=False
            )
            return step_result

        # Extrair informações da tool
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_kwargs = parse_function_args(response)

        self.to_console("Tool Call", f"Name: {tool_name}\nArgs: {tool_kwargs}\nMessage: {response.content}", "magenta")
        tool_result = run_tool_from_response(response, tools=self.tools)
        
        # Extrair informações do response para criar a mensagem de tool
        tool_call_info = {
            "id": response.tool_calls[0]["id"],
            "name": response.tool_calls[0]["name"]
        }
        tool_result_msg = self.tool_call_message_langchain(tool_call_info, tool_result)
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

    def tool_call_message_langchain(self, tool_call: dict, tool_result: ToolResult):
        """Cria mensagem de resposta da tool para LangChain."""
        return {
            "tool_call_id": tool_call.get("id", "unknown"),
            "role": "tool",
            "name": tool_call["name"],
            "content": tool_result.content,
        }

    def _convert_to_langchain_messages(self, messages: List[Dict[str, Any]]):
        """
        Converte mensagens do formato OpenAI para LangChain mantendo compatibilidade total.
        
        Suporta:
        - Mensagens system, user, assistant e tool
        - Tool calls com IDs automáticos quando ausentes
        - Normalização de argumentos de tool calls
        - Agrupamento inteligente de tool calls com suas respostas
        """
        langchain_messages = []
        processed_tool_message_ids = set()  # Track tool messages já processadas
        
        for i, msg in enumerate(messages):
            role = msg["role"]
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
                
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
                
            elif role == "assistant":
                # Verificar se há tool calls
                tool_calls_data = msg.get("tool_calls")
                
                if tool_calls_data:
                    # Processar e normalizar tool calls
                    normalized_tool_calls = []
                    tool_call_ids = []
                    
                    for tc in tool_calls_data:
                        # Normalizar estrutura do tool call
                        normalized_tc = {
                            "name": tc.get("name", tc.get("function", {}).get("name", "")),
                            "args": tc.get("args", tc.get("arguments", tc.get("function", {}).get("arguments", {}))),
                            "id": tc.get("id", str(uuid.uuid4())),
                        }
                        
                        # Manter type se existir (compatibilidade)
                        if "type" in tc:
                            normalized_tc["type"] = tc["type"]
                        
                        normalized_tool_calls.append(normalized_tc)
                        tool_call_ids.append(normalized_tc["id"])
                    
                    # Criar AIMessage com tool calls
                    langchain_messages.append(AIMessage(
                        content=content,
                        tool_calls=normalized_tool_calls
                    ))
                    
                    # Buscar mensagens de tool correspondentes nas próximas mensagens
                    for j in range(i + 1, len(messages)):
                        next_msg = messages[j]
                        
                        if next_msg["role"] == "tool":
                            tool_call_id = next_msg.get("tool_call_id")
                            
                            # Se esta tool message responde a um dos tool calls atuais
                            if tool_call_id in tool_call_ids and tool_call_id not in processed_tool_message_ids:
                                langchain_messages.append(ToolMessage(
                                    content=next_msg.get("content", ""),
                                    tool_call_id=tool_call_id
                                ))
                                processed_tool_message_ids.add(tool_call_id)
                        
                        # Parar se encontrarmos outra mensagem que não seja tool
                        elif next_msg["role"] != "tool":
                            break
                else:
                    # Mensagem normal de assistant sem tool calls
                    langchain_messages.append(AIMessage(content=content))
                    
            elif role == "tool":
                # Só processar mensagens de tool que não foram agrupadas com assistant messages
                tool_call_id = msg.get("tool_call_id")
                
                if tool_call_id not in processed_tool_message_ids:
                    # Gerar ID se não existir (fallback para casos edge)
                    if not tool_call_id:
                        tool_call_id = str(uuid.uuid4())
                    
                    langchain_messages.append(ToolMessage(
                        content=content,
                        tool_call_id=tool_call_id
                    ))
                    processed_tool_message_ids.add(tool_call_id)
        
        return langchain_messages