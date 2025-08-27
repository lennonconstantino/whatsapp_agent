from typing import Type
from pydantic import BaseModel

from app.domain.tools.tool import Tool, ToolResult

class ReportSchema(BaseModel):
    report: str

def report_function(report: ReportSchema) -> str:
    return report.report

class ReportTool(Tool):
    name: str = "report_tool"
    description: str = "Report the results of your work or answer user questions"
    args_schema: Type[BaseModel] = ReportSchema
    model: Type[BaseModel] = ReportSchema
    parse_model: bool = True 
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, input_data: ReportSchema) -> str:
        return report_function(input_data)

report_tool = ReportTool()
