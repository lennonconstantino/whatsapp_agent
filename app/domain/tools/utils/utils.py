from langchain_core.utils.function_calling import _rm_titles
from typing import Type, Optional
from langchain_core.utils.json_schema import dereference_refs
from pydantic import BaseModel
from typing import Type
from langchain_core.tools import tool
from langchain_core.tools import BaseTool

from pydantic import BaseModel

def convert_to_openai_tool(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
) -> dict:
    """Converts a Pydantic model to a function description for the OpenAI API."""
    function = convert_pydantic_to_openai_function(
        model, name=name, description=description
    )
    return {"type": "function", "function": function}


def convert_to_langchain_tool(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
) -> dict:
    """Converts a Pydantic model to a LangChain tool schema."""
    schema = model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema()
    
    # Resolver referências para compatibilidade com Gemini
    try:
        resolved_schema = dereference_refs(schema)
        # Remover definições que podem causar problemas
        resolved_schema.pop("definitions", None)
        resolved_schema.pop("$defs", None)
    except Exception:
        # Se falhar, usar schema original
        resolved_schema = schema
    
    return {
        "type": "function",
        "function": {
            "name": name or model.__name__,
            "description": description or resolved_schema.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": resolved_schema.get("properties", {}),
                "required": resolved_schema.get("required", []),
            }
        }
    }

def convert_pydantic_to_openai_function(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rm_titles: bool = True,
) -> dict:
    """Converts a Pydantic model to a function description for the OpenAI API."""

    model_schema = model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema()
    schema = dereference_refs(model_schema)
    schema.pop("definitions", None)
    title = schema.pop("title", "")
    default_description = schema.pop("description", "")
    return {
        "name": name or title,
        "description": description or default_description,
        "parameters": _rm_titles(schema) if rm_titles else schema,
    }

def convert_langchain_to_openai_tool(tool: BaseTool) -> dict:
    """Converts a LangChain tool to OpenAI function format."""
    if hasattr(tool, 'args_schema') and tool.args_schema:
        schema = tool.args_schema.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": _rm_titles(schema)
            }
        }
    else:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }