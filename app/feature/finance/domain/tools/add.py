from typing import Type
from pydantic import BaseModel
from sqlmodel import Session

from app.domain.tools.base import Tool, ToolResult

from app.feature.finance.persistence.models import *
from app.feature.finance.persistence.db import engine

from langchain_core.tools import BaseTool

class AddExpenseTool(BaseTool):
    name: str = "add_expense"
    description: str = "Add an expense to the database. The tax rate is 0.19. User provides net amount, gross amount is calculated."
    args_schema: Type[BaseModel] = Expense
    
    def _run(self, **kwargs) -> ToolResult:
        expense = Expense.model_validate(kwargs)
        return add_row_to_table(expense)
    
    def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)

class AddRevenueTool(BaseTool):
    name: str = "add_revenue"
    description: str = "Add a revenue entry to the database. The tax rate is 0.19. User provides gross_amount, net_amount is calculated."
    args_schema: Type[BaseModel] = Revenue
    
    def _run(self, **kwargs) -> ToolResult:
        revenue = Revenue.model_validate(kwargs)
        return add_row_to_table(revenue)
    
    def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)

class AddCustomerTool(BaseTool):
    name: str = "add_customer"
    description: str = "Add a customer to the database"
    args_schema: Type[BaseModel] = Customer
    
    def _run(self, **kwargs) -> ToolResult:
        customer = Customer.model_validate(kwargs)
        return add_row_to_table(customer)
    
    def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)

def add_row_to_table(model_instance: SQLModel):
    with Session(engine) as session:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)
    return f"Successfully added {model_instance} to the table"

def add_entry_to_table(sql_model: Type[SQLModel]):
    # return a Callable that takes a SQLModel instance and adds it to the table
    return lambda **data: add_row_to_table(model_instance=sql_model.model_validate(data))

#TODO
# def create_add_data_sql_tool(
#         model: Type[SQLModel],
#         name: str = None,
#         description: str = None,
#         exclude_keys: list[str] = ["id"]
# ) -> Tool:
#     return Tool(
#         model=model,
#         function=add_entry_to_table(model),
#         name=name,
#         description=description,
#         exclude_keys=exclude_keys
#     )

# add_expense_tool = create_add_data_sql_tool(Expense)
# add_revenue_tool = create_add_data_sql_tool(Revenue)
# add_time_tracking_tool = create_add_data_sql_tool(TimeTracking)
# add_employee_tool = create_add_data_sql_tool(Employee)
# add_customer_tool = create_add_data_sql_tool(Customer)
# add_invoice_tool = create_add_data_sql_tool(Invoice)
