from typing import Type
from pydantic import BaseModel
from sqlmodel import Session

from app.domain.tools.tool import Tool, ToolResult

from app.feature.finance.persistence.models import *
from app.feature.finance.persistence.db import engine

def add_row_to_table(model_instance: SQLModel):
    with Session(engine) as session:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)
    return f"Successfully added {model_instance} to the table"

def add_entry_to_table(sql_model: Type[SQLModel]):
    # return a Callable that takes a SQLModel instance and adds it to the table
    return lambda **data: add_row_to_table(model_instance=sql_model.model_validate(data))

class AddExpenseTool(Tool):
    name: str = "add_expense"
    description: str = "Add an expense to the database. The tax rate is 0.19. User provides net amount, gross amount is calculated."
    args_schema: Type[BaseModel] = Expense
    model: Type[BaseModel] = Expense

    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)

    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
        expense = Expense.model_validate(kwargs)
        return add_row_to_table(expense)

class AddRevenueTool(Tool):
    name: str = "add_revenue"
    description: str = "Add a revenue entry to the database. The tax rate is 0.19. User provides gross_amount, net_amount is calculated."
    args_schema: Type[BaseModel] = Revenue
    model: Type[BaseModel] = Revenue
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    async def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
        revenue = Revenue.model_validate(kwargs)
        return add_row_to_table(revenue) 

class AddCustomerTool(Tool):
    name: str = "add_customer"
    description: str = "Add a customer to the database"
    args_schema: Type[BaseModel] = Customer
    model: Type[BaseModel] = Customer
    
    def _run(self, **kwargs) -> ToolResult:
        return super()._run(**kwargs)
    
    def _arun(self, **kwargs) -> ToolResult:
        return self._run(**kwargs)
    
    def execute(self, **kwargs) -> ToolResult:
        customer = Customer.model_validate(kwargs)
        return add_row_to_table(customer)        

add_expense_tool = AddExpenseTool()
add_revenue_tool = AddRevenueTool()
add_customer_tool = AddCustomerTool()
