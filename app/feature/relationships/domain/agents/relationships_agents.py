from app.domain.agents.task import TaskAgent
from app.domain.agents.routing import RoutingAgent
from app.domain.tools.base import Tool

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
    system_message=TASK_SYSTEM_MESSAGE
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
