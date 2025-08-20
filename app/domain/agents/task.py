from typing import Type, Callable, Optional

from app.domain.agents.base import OpenAIAgent
from app.domain.tools.base import Tool
from app.domain.tools.report_tool import report_tool
from pydantic import BaseModel, ConfigDict, Field

from app.domain.tools.utils.system_message_factory import StaticSystemMessageProvider, SystemMessageProvider
from app.domain.tools.utils.utils import convert_to_openai_tool

DEFAULT_SYSTEM_MESSAGE = """"""

class EmptyArgModel(BaseModel):
    pass

class TaskAgent(BaseModel):
    name: str
    description: str
    arg_model: Type[BaseModel] = EmptyArgModel
    access_roles: list[str] = ["all"]

    create_context: Callable = None
    create_user_context: Callable = None
    tool_loader: Callable = None

    # Novo: Provedor de mensagem do sistema (mantém compatibilidade)
    system_message_provider: SystemMessageProvider = Field(
        default_factory=lambda: StaticSystemMessageProvider(DEFAULT_SYSTEM_MESSAGE)
    )
    
    # Mantido para compatibilidade (deprecated)
    system_message: Optional[str] = None

    tools: list[Tool]
    examples: list[dict] = None
    routing_example: list[dict] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        # Compatibilidade: se system_message foi passado, usar StaticProvider
        if 'system_message' in data and data['system_message'] is not None:
            if 'system_message_provider' not in data:
                data['system_message_provider'] = StaticSystemMessageProvider(data['system_message'])
        
        super().__init__(**data)

    def load_agent(self, **kwargs) -> OpenAIAgent:

        input_kwargs = self.arg_model(**kwargs)
        kwargs = input_kwargs.dict()

        context = self.create_context(**kwargs) if self.create_context else None
        user_context = self.create_user_context(**kwargs) if self.create_user_context else None

        if self.tool_loader:
            self.tools.extend(self.tool_loader(**kwargs))

        if report_tool not in self.tools:
            self.tools.append(report_tool)

        return OpenAIAgent(
            tools=self.tools,
            context=context,
            user_context=user_context,
            system_message=self.system_message,
            examples=self.examples,
        )

    @property
    def openai_tool_schema(self):
        return convert_to_openai_tool(self.arg_model, name=self.name, description=self.description)
