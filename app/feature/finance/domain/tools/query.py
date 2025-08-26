from typing import Type, Union, Literal

from pydantic import BaseModel
from sqlmodel import Session, select, SQLModel

from app.domain.tools.base import ToolResult

from app.feature.finance.persistence.models import *
from app.feature.finance.persistence.db import engine

from langchain_core.tools import BaseTool
from langchain_core.tools import tool

TABLES = {
    "expense": Expense,
    "revenue": Revenue,
    "customer": Customer
}


'''
class WhereStatement(BaseModel):
    column: str
    operator: Literal["eq", "gt", "lt", "gte", "lte", "ne", "ct"]
    value: str

class QueryConfig(BaseModel):
    table_name: str
    select_columns: list[str] = ["*"]  # Valor padrão para retornar todas as colunas
    where: list[Union[WhereStatement, None]] = []  # Tornar opcional com valor padrão

def query_data_function(query_config: QueryConfig) -> ToolResult:
    """Query the database via natural language."""
    if query_config.table_name not in TABLES:
        return ToolResult(content=f"Table name {query_config.table_name} not found in database models", success=False)

    sql_model = TABLES[query_config.table_name]

    # query_config = validate_query_config(query_config, sql_model)
    data = sql_query_from_config(query_config, sql_model)

    return ToolResult(content=f"Query results: {data}", success=True)

query_data_tool = tool(
    name="query_data_tool",
    description="Query financial data from the database. Required: table_name (expense, revenue, customer). Optional: select_columns (defaults to all columns), where conditions for filtering. Example: {'table_name': 'expense'} will return all expense records with all columns.",
    model=QueryConfig,
    function=query_data_function,
    parse_model=True,
    validate_missing=False  # Desabilitar validação para campos opcionais
)

# === Helper ===

def sql_query_from_config(
        query_config: QueryConfig,
        sql_model: Type[SQLModel]):

    with Session(engine) as session:
        selection = []
        
        # Se select_columns é ["*"] ou vazio, selecionar todas as colunas
        if not query_config.select_columns or query_config.select_columns == ["*"]:
            selection = [sql_model]
        else:
            for column in query_config.select_columns:
                if column not in sql_model.__annotations__:
                    return f"Column {column} not found in model {sql_model.__name__}"
                selection.append(getattr(sql_model, column))
        
        statement = select(*selection)
        wheres = query_config.where
        if wheres:
            for where in wheres:

                if not where:
                    continue

                if where.column not in sql_model.__annotations__:  # noqa
                    return f"Column {where['column']} not found in model {sql_model.__name__}"

                elif where.operator == "eq":
                    statement = statement.where(getattr(sql_model, where.column) == where.value)
                elif where.operator == "gt":
                    statement = statement.where(getattr(sql_model, where.column) > where.value)
                elif where.operator == "lt":
                    statement = statement.where(getattr(sql_model, where.column) < where.value)
                elif where.operator == "gte":
                    statement = statement.where(getattr(sql_model, where.column) >= where.value)
                elif where.operator == "lte":
                    statement = statement.where(getattr(sql_model, where.column) <= where.value)
                elif where.operator == "ne":
                    statement = statement.where(getattr(sql_model, where.column) != where.value)
                elif where.operator == "ct":
                    statement = statement.where(getattr(sql_model, where.column).contains(where.value))

        result = session.exec(statement)
        data = result.all()
        try:
            data = [repr(d) for d in data]
        except:
            pass
    return data
'''

class WhereStatement(BaseModel):
    column: str = Field(description="Nome da coluna para filtrar")
    operator: Literal["eq", "gt", "lt", "gte", "lte", "ne", "ct"] = Field(description="Operador de comparação")
    value: str = Field(description="Valor para comparação")

class QueryConfig(BaseModel):
    table_name: str = Field(description="Nome da tabela (expense, revenue, customer)")
    select_columns: list[str] = Field(default=["*"], description="Colunas a selecionar")
    where: list[Union[WhereStatement, None]] = Field(default=[], description="Condições de filtro")

class QueryDataTool(BaseTool):
    name: str = "query_data_tool"
    description: str = "Query financial data from the database. Required: table_name (expense, revenue, customer). Optional: select_columns (defaults to all columns), where conditions for filtering."
    args_schema: Type[BaseModel] = QueryConfig
    
    def _run(self, query_config: QueryConfig) -> ToolResult:
        # Manter lógica existente da função query_data_function
        if query_config.table_name not in TABLES:
            return ToolResult(content=f"Table name {query_config.table_name} not found in database models", success=False)
        
        return query_data_function(query_config)
        
    def _arun(self, query_config: QueryConfig) -> ToolResult:
        return self._run(query_config)

def sql_query_from_config(
        query_config: QueryConfig,
        sql_model: Type[SQLModel]):

    with Session(engine) as session:
        selection = []
        
        # Se select_columns é ["*"] ou vazio, selecionar todas as colunas
        if not query_config.select_columns or query_config.select_columns == ["*"]:
            selection = [sql_model]
        else:
            for column in query_config.select_columns:
                if column not in sql_model.__annotations__:
                    return f"Column {column} not found in model {sql_model.__name__}"
                selection.append(getattr(sql_model, column))
        
        statement = select(*selection)
        wheres = query_config.where
        if wheres:
            for where in wheres:

                if not where:
                    continue

                if where.column not in sql_model.__annotations__:  # noqa
                    return f"Column {where['column']} not found in model {sql_model.__name__}"

                elif where.operator == "eq":
                    statement = statement.where(getattr(sql_model, where.column) == where.value)
                elif where.operator == "gt":
                    statement = statement.where(getattr(sql_model, where.column) > where.value)
                elif where.operator == "lt":
                    statement = statement.where(getattr(sql_model, where.column) < where.value)
                elif where.operator == "gte":
                    statement = statement.where(getattr(sql_model, where.column) >= where.value)
                elif where.operator == "lte":
                    statement = statement.where(getattr(sql_model, where.column) <= where.value)
                elif where.operator == "ne":
                    statement = statement.where(getattr(sql_model, where.column) != where.value)
                elif where.operator == "ct":
                    statement = statement.where(getattr(sql_model, where.column).contains(where.value))

        result = session.exec(statement)
        data = result.all()
        try:
            data = [repr(d) for d in data]
        except:
            pass
    return data

def query_data_function(query_config: QueryConfig) -> ToolResult:
    """Query the database via natural language."""
    if query_config.table_name not in TABLES:
        return ToolResult(content=f"Table name {query_config.table_name} not found in database models", success=False)

    sql_model = TABLES[query_config.table_name]

    data = sql_query_from_config(query_config, sql_model)

    return ToolResult(content=f"Query results: {data}", success=True)
    

# Substituir a instância antiga
query_data_tool = QueryDataTool()