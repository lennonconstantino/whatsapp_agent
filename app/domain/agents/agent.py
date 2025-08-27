import colorama
from typing import Dict, Any, List
from colorama import Fore
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app.domain.agents.utils import parse_function_args, run_tool_from_response
from app.infrastructure.llm import LLM, models
from app.domain.tools.tool import Tool, ToolResult

class StepResult(BaseModel):
    event: str
    content: str
    success: bool

SYSTEM_MESSAGE = """# Task Execution Agent with Tool Management

You are a specialized task execution agent responsible for completing objectives using available tools and providing comprehensive reports. Your mission is to strategically utilize tools, learn from feedback, and ensure all tasks conclude with proper documentation.

## Core Responsibilities

**Primary Objective**: Complete assigned tasks efficiently while maintaining detailed reporting of all outcomes, whether successful or unsuccessful.

**Tool Selection Strategy**: Analyze each task requirement against available tool capabilities to make optimal choices that maximize success probability.

## Execution Workflow

### Step 1: Task Analysis & Planning

**Thought Process**: 
- Evaluate the task complexity and requirements
- Identify the most suitable tool based on:
  - Task nature and complexity
  - Tool capabilities and limitations  
  - Available information sufficiency
- If the task can be completed with provided information alone, proceed directly to reporting

### Step 2: Tool Execution
**Action Selection**:
- **Direct Completion**: If sufficient information is available, use `report_tool` immediately with complete results
- **Tool Utilization**: Deploy the most appropriate specialized tool for complex tasks requiring external processing
- **Strategic Progression**: Build upon previous tool outputs when multiple steps are needed

### Step 3: Outcome Reporting
**Mandatory Reporting**: Every task execution must conclude with `report_tool` usage containing:

**For Successful Completion**:
- Detailed summary of work performed
- Complete results and findings  
- Key insights or answers derived
- Methodology used and tools deployed

**For Incomplete/Failed Tasks**:
- Clear explanation of encountered challenges
- Specific reasons for task incompletion
- Steps attempted and their outcomes
- Recommendations for resolution (if applicable)

## Operational Guidelines

### Tool Usage Rules
- **Single Tool Calls**: Execute only ONE tool per interaction cycle
- **Sequential Processing**: Wait for tool feedback before proceeding to next action
- **Adaptive Strategy**: Modify approach based on received feedback and results

### Quality Standards
- **Thoroughness**: Provide comprehensive information in all reports
- **Clarity**: Use clear, specific language avoiding ambiguity
- **Completeness**: Address all aspects of the original task requirement
- **Professional Tone**: Maintain formal, objective communication style

### Feedback Integration
**Continuous Improvement**: Each tool execution provides valuable feedback that should inform:
- Future tool selection decisions
- Strategy refinement for similar tasks
- Problem-solving approach optimization
- Alternative solution identification

## Error Handling & Recovery

**Challenge Resolution Process**:
1. **Identify**: Clearly define the specific obstacle or limitation encountered
2. **Analyze**: Determine root cause and assess alternative approaches  
3. **Adapt**: Modify strategy using different tools or methodologies
4. **Report**: Document the challenge and resolution attempts comprehensively

**Escalation Protocol**: When tasks cannot be completed despite multiple approaches, provide detailed failure analysis including attempted solutions and recommendations.

## Success Metrics

**Task Completion Indicators**:
- Objective fully achieved with supporting evidence
- Comprehensive report generated with actionable insights  
- All questions answered with sufficient detail
- Clear documentation of methodology and results

**Quality Benchmarks**:
- Accuracy of information provided
- Completeness of task coverage
- Clarity of communication
- Strategic tool utilization efficiency

---

## Context Information for Current Task:
{context}

---

**Remember**: Your effectiveness is measured not just by task completion, but by the quality of insights, thoroughness of reporting, and strategic use of available tools. Every interaction should move closer to comprehensive objective fulfillment."""

class Agent:

    def __init__(
            self,
            tools: List[Tool],
            system_message: str = SYSTEM_MESSAGE,
            llm: Dict[str, Any] = models,
            max_steps: int = 5,
            verbose: bool = True,
            examples: List[dict] = None,
            context: str = None,
            user_context: str = None
    ):
        self.tools = tools
        self.llm = llm
        self.system_message = system_message
        self.memory = []
        self.step_history = []
        self.max_steps = max_steps
        self.verbose = verbose
        self.examples = examples or []
        self.context = context or ""
        self.user_context = user_context

    def to_console(self, tag: str, message: str, color: str = "green"):
        if self.verbose:
            color_prefix = Fore.__dict__[color.upper()]
            print(color_prefix + f"{tag}: {message}{colorama.Style.RESET_ALL}")

    def run(self, user_input: str, context: str = None):
        # Converter tools para formato LangChain
        langchain_tools = [tool.langchain_tool_schema for tool in self.tools]
        system_message = self.system_message.format(context=context)

        if self.user_context:
            context = context if context else self.user_context

        if context:
            user_input = f"{context}\n---\n\nUser Message: {user_input}"

        self.to_console("START", f"Starting Agent with Input:\n'''{user_input}'''")

        self.step_history = [
            {"role": "system", "content": system_message},
            *self.examples,
            {"role": "user", "content": user_input}
        ]

        step_result = None
        i = 0

        while i < self.max_steps:
            step_result = self.run_step(self.step_history, langchain_tools)
            if step_result.event == "finish":
                break
            elif step_result.event == "error":
                self.to_console(step_result.event, step_result.content, "red")
            else:
                self.to_console(step_result.event, step_result.content, "yellow")

            i += 1

        self.to_console("Final Result", step_result.content, "green")
        return step_result.content

    def run_step(self, messages: List[dict], tools):
        # Converter mensagens para formato LangChain
        langchain_messages = self._convert_to_langchain_messages(messages)

        # Bind tools e invocar
        model = self.llm[LLM]
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(langchain_messages)

        # Verificar múltiplas tool calls
        if response.tool_calls and len(response.tool_calls) > 1:
            messages = [
                *self.step_history,
                {"role": "user", "content": "Error: Please return only one tool call at a time."}
            ]
            return self.run_step(messages, tools)

        # Adicionar mensagem do assistente ao histórico
        assistant_message = {
            "role": "assistant", 
            "content": response.content,
            "tool_calls": response.tool_calls if response.tool_calls else None
        }
        self.step_history.append(assistant_message)
        
        # Verificar se há tool call
        if not response.tool_calls:
            msg = response.content
            step_result = StepResult(
                event="error", 
                content=f"No tool calls were returned.\nMessage: {msg}", 
                success=False
            )
            return step_result

        # Extrair informações da tool
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_kwargs = parse_function_args(response)

        self.to_console("Tool Call", f"Name: {tool_name}\nArgs: {tool_kwargs}\nMessage: {response.content}", "magenta")
        tool_result = run_tool_from_response(response, tools=self.tools)
        
        # Extrair informações do response para criar a mensagem de tool
        tool_call_info = {
            "id": response.tool_calls[0]["id"],
            "name": response.tool_calls[0]["name"]
        }
        tool_result_msg = self.tool_call_message_langchain(tool_call_info, tool_result)
        self.step_history.append(tool_result_msg)

        # Verificar se é report_tool para finalizar
        if tool_name == "report_tool":
            step_result = StepResult(
                event="finish",
                content=tool_result.content,
                success=True
            )
            return step_result

        # Processar resultado da tool
        if tool_result.success:
            step_result = StepResult(
                event="tool_result",
                content=tool_result.content,
                success=True
            )
        else:
            step_result = StepResult(
                event="error",
                content=tool_result.content,
                success=False
            )

        return step_result

    def tool_call_message_langchain(self, tool_call: dict, tool_result: ToolResult):
        """Cria mensagem de resposta da tool para LangChain."""
        return {
            "tool_call_id": tool_call.get("id", "unknown"),
            "role": "tool",
            "name": tool_call["name"],
            "content": tool_result.content,
        }

    def _convert_to_langchain_messages(self, messages: List[dict]):
        """Converte mensagens do formato OpenAI para LangChain."""
        langchain_messages = []
        
        for i, msg in enumerate(messages):
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                # Para mensagens de assistant, verificar se têm tool_calls
                if msg.get("tool_calls"):
                    # Se tem tool_calls, criar AIMessage com tool_calls
                    langchain_messages.append(AIMessage(
                        content=msg["content"],
                        tool_calls=msg["tool_calls"]
                    ))
                    
                    # Verificar se há mensagens de tool correspondentes
                    tool_call_ids = [tc.get("id") for tc in msg["tool_calls"]]
                    for j in range(i + 1, len(messages)):
                        next_msg = messages[j]
                        if (next_msg["role"] == "tool" and 
                            next_msg.get("tool_call_id") in tool_call_ids):
                            # Incluir mensagem de tool que responde a este tool_call
                            langchain_messages.append(ToolMessage(
                                content=next_msg["content"],
                                tool_call_id=next_msg["tool_call_id"]
                            ))
                else:
                    # Mensagem normal de assistant
                    langchain_messages.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "tool":
                # Só incluir mensagens de tool se não foram incluídas acima
                # (elas são incluídas quando processamos mensagens de assistant com tool_calls)
                pass
        
        return langchain_messages