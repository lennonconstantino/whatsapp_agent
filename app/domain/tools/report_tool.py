from typing import Callable, Type
from pydantic import BaseModel, Field

from langchain_core.tools import BaseTool

from app.domain.tools.base import Tool, ToolResult


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