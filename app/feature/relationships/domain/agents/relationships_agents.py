from app.domain.agents.task import TaskAgent
from app.domain.agents.routing import RoutingAgent

from app.feature.relationships.domain.tools.relationships import (
    add_person_tool,
    log_interaction_tool,
    schedule_reminder_tool,
    query_people_tool,
    query_interactions_tool,
    upcoming_reminders_tool,
)

from app.feature.relationships.domain.agents.task import SYSTEM_MESSAGE as TASK_SYSTEM_MESSAGE
from app.feature.relationships.domain.agents.routing import SYSTEM_MESSAGE as ROUTING_SYSTEM_MESSAGE, PROMPT_EXTRA

query_relationships_agent = TaskAgent(
    name="query_relationships_agent",
    description="Agent that can query people, interactions and upcoming reminders",
    tools=[
        query_people_tool,
        query_interactions_tool,
        upcoming_reminders_tool,
    ],
    system_message=TASK_SYSTEM_MESSAGE,
    examples=[
        {
            "role": "user",
            "content": "Who are my contacts?"
        },
        {
            "role": "assistant",
            "content": "I'll search for all your contacts. Since you're asking for a general overview, I'll use the query_people tool without specific filters to return all contacts.",
            "tool_calls": [
                {
                    "id": "call_example_1",
                    "name": "query_people",
                    "args": {}
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_example_1",
            "content": "Found 5 contacts: [Person(id=1, first_name='John', last_name='Doe'), Person(id=2, first_name='Jane', last_name='Smith'), ...]"
        },
        {
            "role": "user",
            "content": "Find contacts with tag 'family'"
        },
        {
            "role": "assistant",
            "content": "I'll search for contacts that have the 'family' tag using the query_people tool.",
            "tool_calls": [
                {
                    "id": "call_example_2",
                    "name": "query_people",
                    "args": {"tag_contains": "family"}
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_example_2",
            "content": "Found 3 contacts with 'family' tag: [Person(id=1, first_name='John', last_name='Doe', tags='family'), Person(id=3, first_name='Mom', last_name='Johnson', tags='family'), Person(id=5, first_name='Dad', last_name='Johnson', tags='family')]"
        }
    ]
)


add_person_agent = TaskAgent(
    name="add_person_agent",
    description="Agent that can add a person to the database",
    tools=[add_person_tool],
    system_message=TASK_SYSTEM_MESSAGE
)


log_interaction_agent = TaskAgent(
    name="log_interaction_agent",
    description="Agent that can log an interaction for a person",
    tools=[log_interaction_tool],
    system_message=TASK_SYSTEM_MESSAGE
)


schedule_reminder_agent = TaskAgent(
    name="schedule_reminder_agent",
    description="Agent that can schedule reminders for a person",
    tools=[schedule_reminder_tool],
    system_message=TASK_SYSTEM_MESSAGE
)


relationships_agent = RoutingAgent(
    tools=[
        query_relationships_agent,
        add_person_agent,
        log_interaction_agent,
        schedule_reminder_agent,
    ],
    system_message=ROUTING_SYSTEM_MESSAGE,
    prompt_extra=PROMPT_EXTRA
)
