from typing import List, Dict, Any
import colorama
#from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.infrastructure.llm import LLM, models
from app.domain.agents.task import TaskAgent

from langchain_core.tools import tool

NOTES = """Important Notes:
Always confirm the completion of the requested operation with the user.
Maintain user privacy and data security throughout the interaction.
If a request is ambiguous or lacks specific details, ask follow-up questions to clarify the user's needs."""

class RoutingAgent:

    def __init__(
            self,
            tools: List[TaskAgent] = None,
            llm: Dict[str, Any] = models,
            system_message: str = "",
            max_steps: int = 5,
            verbose: bool = True,
            prompt_extra: Dict[str, Any] = None,
            examples: List[dict] = None,
            context: str = None
    ):
        self.tools = tools or []
        self.llm = llm
        self.system_message = system_message
        self.memory = []
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.prompt_extra = prompt_extra or {}
        self.examples = self.load_examples(examples)
        self.context = context or ""

    def load_examples(self, examples: List[dict] = None):
        examples = examples or []
        for agent in self.tools:
            examples.extend(agent.routing_example)
        return examples

    def run(self, user_input: str, employee_id: int = None, **kwargs):
        context = kwargs.get("context") or self.context
        if context:
            user_input_with_context = f"{context}\n---\n\nUser Message: {user_input}"
        else:
            user_input_with_context = user_input
            
        self.to_console("START", f"Starting Routing Agent with Input:\n'''{user_input_with_context}'''")
        
        partial_variables = {**self.prompt_extra, "context": context}
        system_message = self.system_message.format(**partial_variables)

        # Converter mensagens para formato LangChain
        messages = [
            SystemMessage(content=system_message),
            *[HumanMessage(content=ex["content"]) if ex["role"] == "user" else AIMessage(content=ex["content"]) for ex in self.examples],
            HumanMessage(content=user_input)
        ]

        # Converter tools para formato LangChain
        tools = [tool.langchain_tool_schema for tool in self.tools]
        # tools = []
        # for agent in self.tools:
        #     if hasattr(agent, 'tools'):
        #         for tool in agent.tools:
        #             #tools.append(tool)
        #             if hasattr(tool, 'function'):
        #                 tools.append(tool)

        # Bind tools e invocar
        model = self.llm[LLM]
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(messages)
        #response = model.invoke_with_tool_calling(messages, tools=tools)
        
        self.step_history.append(response)
        self.to_console("RESPONSE", response.content, color="blue")
        
        # Verificar se há tool calls
        if not response.tool_calls:
            self.to_console("Tool Name", "None")
            self.to_console("Tool Args", "None")
            return response.content
            
        # Extrair informações da tool call
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        self.to_console("Tool Name", tool_name)
        self.to_console("Tool Args", str(tool_args))

        # Preparar e executar o agente
        agent = self.prepare_agent(tool_name, tool_args)
        return agent.run(user_input)

    def prepare_agent(self, tool_name: str, tool_kwargs: Dict[str, Any]):
        for agent in self.tools:
            if agent.name == tool_name:
                input_kwargs = agent.arg_model.model_validate(tool_kwargs)
                return agent.load_agent(**input_kwargs.model_dump())
        raise ValueError(f"Agent {tool_name} not found")

    def to_console(self, tag: str, message: str, color: str = "green"):
        if self.verbose:
            color_prefix = colorama.Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")
