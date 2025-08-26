from typing import Type
from pydantic import BaseModel, Field

#from app.domain.tools.base import Tool
from langchain_core.tools import BaseTool

from app.domain.tools.base import ToolResult

# class ReportSchema(BaseModel):
#     report: str


# def report_function(report: ReportSchema) -> str:
#     return report.report


class ReportSchema(BaseModel):
    report: str = Field(description="Relatório ou resposta para o usuário")

class ReportTool(BaseTool):
    name: str = "report_tool"
    description: str = "Report the results of your work or answer user questions"
    args_schema: Type[BaseModel] = ReportSchema

    def _run(self, report: ReportSchema) -> ToolResult:
        return ToolResult(content=report.report, success=True)
    
    def _arun(self, report: ReportSchema) -> ToolResult:
        return self._run(report)

report_tool = ReportTool()

# report_tool = Tool(
#     name="report_tool",
#     model=ReportSchema,
#     function=report_function,
#     validate_missing=False,
#     parse_model=True
# )
