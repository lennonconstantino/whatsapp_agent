from app.domain.agents.routing import RoutingAgent
from app.domain.agents.utils import generate_query_context
from app.domain.agents.task import TaskAgent

from app.feature.finance.domain.tools.query import query_data_tool
from app.feature.finance.domain.tools.add import add_customer_tool, add_expense_tool, add_revenue_tool
from app.feature.finance.domain.agents.task import SYSTEM_MESSAGE as TASK_SYSTEM_MESSAGE
from app.feature.finance.persistence.models import Expense, Revenue, Customer

from app.feature.finance.domain.agents.routing import SYSTEM_MESSAGE as ROUTING_SYSTEM_MESSAGE, PROMPT_EXTRA

query_task_agent = TaskAgent(
    name="query_agent",
    description="An agent that can perform queries on multiple data sources",
    create_user_context=lambda: generate_query_context(Expense, Revenue, Customer),
    tools=[query_data_tool],
    system_message=TASK_SYSTEM_MESSAGE,
    # examples=[
    #     {
    #         "role": "user",
    #         "content": "What are my expenses?"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "I'll check your expenses using the database tool.",
    #         "tool_calls": [{"name": "query_data_tool", "args": {"table": "expense"}}]
    #     }
    # ]
    # examples = [
    #     {
    #         "role": "user",
    #         "content": "Show my expenses"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "I'll check your expenses.",
    #         "tool_calls": [{"name": "query_data_tool", "args": {"table_name": "expense"}}]
    #     },
    #     {
    #         "role": "tool",
    #         "content": "Expenses found: Office supplies $300, Cloud hosting $150",
    #         "tool_call_id": "123"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "Here are your expenses: Office supplies $300, Cloud hosting $150",
    #         "tool_calls": [{"name": "report_tool", "args": {"report": "Expenses retrieved successfully"}}]
    #     }
    # ]
)

add_expense_agent = TaskAgent(
    name="add_expense_agent",
    description="An agent that can add an expense to the database",
    create_user_context=lambda: generate_query_context(Expense) + "\nRemarks: The tax rate is 0.19. The user provide the net amount you need to calculate the gross amount.",
    tools=[add_expense_tool],
    system_message=TASK_SYSTEM_MESSAGE
)

add_revenue_agent = TaskAgent(
    name="add_revenue_agent",
    description="An agent that can add a revenue entry to the database",
    create_user_context=lambda: generate_query_context(Revenue) + "\nRemarks: The tax rate is 0.19. The user provide the gross_amount you should use the tax rate to calculate the net_amount.",
    tools=[add_revenue_tool],
    system_message=TASK_SYSTEM_MESSAGE
)

add_customer_agent = TaskAgent(
    name="add_customer_agent",
    description="An agent that can add a customer to the database",
    create_user_context=lambda: generate_query_context(Customer),
    tools=[add_customer_tool],
    system_message=TASK_SYSTEM_MESSAGE
)

finance_agent = RoutingAgent(
    tools=[
        query_task_agent,
        add_expense_agent,
        add_revenue_agent,
        add_customer_agent
    ],
    system_message=ROUTING_SYSTEM_MESSAGE,
    prompt_extra=PROMPT_EXTRA
)
