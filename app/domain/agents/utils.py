from datetime import datetime
from typing import Type
import types
import typing

import sqlalchemy
from pydantic import BaseModel

def parse_function_args(response):
    """Parse function arguments from LangChain AIMessage response"""
    if not response.tool_calls:
        return {}
    return response.tool_calls[0]["args"]

def get_tool_from_response(response, tools):
    """Get tool from LangChain AIMessage response"""
    tool_name = response.tool_calls[0]["name"]
    for t in tools:
        if t.name == tool_name:
            return t
    raise ValueError(f"Tool {tool_name} not found in tools list.")

def run_tool_from_response(response, tools):
    tool = get_tool_from_response(response, tools)
    tool_kwargs = parse_function_args(response)
    return tool._run(**tool_kwargs)

def orm_model_to_string(input_model_cls: Type[BaseModel]):
    """Get the ORM model string from the input model"""

    def process_field(key, value):
        if key.startswith("__"):
            return None
        if isinstance(value, typing._GenericAlias):
            if value.__origin__ == sqlalchemy.orm.base.Mapped:
                return None
            if isinstance(value, typing._AnnotatedAlias):  # noqa
                return key, value.__origin__
            elif isinstance(value, typing._UnionGenericAlias) or isinstance(value, types.UnionType):
                return key, value.__args__[0]
        return key, value

    fields = dict(filter(None, (process_field(k, v) for k, v in input_model_cls.__annotations__.items())))
    return ", ".join([f"{k} = <{v.__name__}>" for k, v in fields.items()])

def weekday_by_date(date: datetime):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

def date_to_string(date: datetime):
    return f"{weekday_by_date(date)} {parse_date(date)}"

def parse_date(date: datetime):
    return date.strftime("%Y-%m-%d")

def generate_query_context(*table_models) -> str:
    today = f"Today is {date_to_string(datetime.now())}"
    context_str = "You can access the following tables in database:\n"
    for table in table_models:
        context_str += f" - {table.__name__.lower()}: {orm_model_to_string(table)}\n"
    return f"{today}\n{context_str}"
