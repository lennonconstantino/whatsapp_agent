from abc import abstractmethod
from typing import Any, Optional, Type, Callable, Union

from app.domain.tools.utils.utils import convert_to_openai_tool, convert_to_langchain_tool
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel

from langchain_core.tools import BaseTool

class ToolResult(BaseModel):
    content: str
    success: bool


class Tool(BaseTool):
    name: str
    description: str = ""
    args_schema: Optional[Type[BaseModel]] = None
    #
    model: Union[Type[BaseModel], Type[SQLModel], None]
    function: Callable
    validate_missing: bool = True
    parse_model: bool = False
    exclude_keys: list[str] = ["id"]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, **kwargs) -> ToolResult:
        missing_values = self.validate_input(**kwargs)
        if missing_values:
            content = f"Missing values: {', '.join(missing_values)}"
            return ToolResult(content=content, success=False)

        if self.parse_model:
            if hasattr(self.model, "model_validate"):
                input_ = self.model.model_validate(kwargs)
            else:
                input_ = self.model(**kwargs)
            result = self.execute(input_)
        else:
            result = self.execute(**kwargs)

        return ToolResult(content=str(result), success=True)
    
    def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)

    def validate_input(self, **kwargs):
        if not self.validate_missing or not self.model:
            return []
        model_keys = set(self.model.__annotations__.keys()) - set(self.exclude_keys)
        input_keys = set(kwargs.keys())
        missing_values = model_keys - input_keys
        return list(missing_values)

    @property
    def openai_tool_schema(self):
        schema = convert_to_openai_tool(self.model)
        schema["function"]["name"] = self.name
        if schema["function"]["parameters"].get("required"):
            del schema["function"]["parameters"]["required"]
        schema["function"]["parameters"]["properties"] = {
            key: value for key, value in schema["function"]["parameters"]["properties"].items()
            if key not in self.exclude_keys
        }
        return schema

    @property
    def langchain_tool_schema(self):
        """Retorna o schema da tool no formato LangChain."""
        schema = convert_to_langchain_tool(self.model)
        schema["function"]["name"] = self.name
        if schema["function"]["parameters"].get("required"):
            del schema["function"]["parameters"]["required"]
        schema["function"]["parameters"]["properties"] = {
            key: value for key, value in schema["function"]["parameters"]["properties"].items()
            if key not in self.exclude_keys
        }
        return schema
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Método abstrato que deve ser implementado pelas classes filhas"""
        pass


class ReportSchema(BaseModel):
    report: str


def report_function(report: ReportSchema) -> str:
    return report.report


# report_tool = Tool(
#     name="report_tool",
#     model=ReportSchema,
#     function=report_function,
#     validate_missing=False,
#     parse_model=True
# )

class ReportTool(Tool):
    name: str = "report_tool"
    description: str = "Report the results of your work or answer user questions"
    args_schema: Type[BaseModel] = ReportSchema
    model: Type[BaseModel] = ReportSchema
    function: Callable = None
    parse_model: bool = True 
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> str:
        if hasattr(self, 'parse_model') and self.parse_model:
            report = ReportSchema.model_validate(kwargs)
        else:
            report = ReportSchema(**kwargs)
        
        return report_function(report)

report_tool = ReportTool()
