from typing import Type, Callable, Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.domain.agents.base import Agent
from app.domain.tools.base import Tool
from app.domain.tools.report_tool import report_tool
from app.domain.tools.utils.system_message_factory import StaticSystemMessageProvider, SystemMessageProvider
from app.domain.tools.utils.utils import convert_to_langchain_tool

from langchain_core.tools import BaseTool

DEFAULT_SYSTEM_MESSAGE = """"""

class EmptyArgModel(BaseModel):
    pass

class TaskAgent(BaseModel):
    name: str
    description: str
    arg_model: Type[BaseModel] = EmptyArgModel
    access_roles: List[str] = Field(default_factory=lambda: ["all"])

    create_context: Optional[Callable] = None
    create_user_context: Optional[Callable] = None
    tool_loader: Optional[Callable] = None

    # Provedor de mensagem do sistema
    system_message_provider: SystemMessageProvider = Field(
        default_factory=lambda: StaticSystemMessageProvider(DEFAULT_SYSTEM_MESSAGE)
    )
    
    # Mantido para compatibilidade (deprecated)
    system_message: Optional[str] = None

    #tools: List[Tool]
    tools: List[BaseTool]  # Mudança: agora aceita BaseTool do LangChain
    examples: Optional[List[dict]] = None
    routing_example: List[dict] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        # Compatibilidade: se system_message foi passado, usar StaticProvider
        if 'system_message' in data and data['system_message'] is not None:
            if 'system_message_provider' not in data:
                data['system_message_provider'] = StaticSystemMessageProvider(data['system_message'])
        
        super().__init__(**data)

    def load_agent(self, **kwargs) -> Agent:
        input_kwargs = self.arg_model(**kwargs)
        kwargs = input_kwargs.model_dump()

        context = self.create_context(**kwargs) if self.create_context else None
        user_context = self.create_user_context(**kwargs) if self.create_user_context else None

        if self.tool_loader:
            self.tools.extend(self.tool_loader(**kwargs))

        if report_tool not in self.tools:
            self.tools.append(report_tool)

        return Agent(
            tools=self.tools,
            context=context,
            user_context=user_context,
            system_message=self.system_message,
            examples=self.examples,
        )

    @property
    def langchain_tool_schema(self):
        """Retorna o schema da tool no formato LangChain."""
        #return convert_to_langchain_tool(self.arg_model, name=self.name, description=self.description)
        return self.tools  # Agora retorna diretamente as ferramentas LangChain

    @property
    def openai_tool_schema(self):
        """Mantido para compatibilidade - retorna o schema da tool no formato OpenAI."""
        # Import local para evitar dependência circular
        from app.domain.tools.utils.utils import convert_to_openai_tool
        return convert_to_openai_tool(self.arg_model, name=self.name, description=self.description)
