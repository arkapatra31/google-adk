import asyncio
import json
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from custom_routing_agent.agents import route_agent, travel_itinerary_agent, email_writer_agent
from custom_routing_agent.routing import Router

APP_NAME = "custom_routing_agent"
USER_ID = "user_1"
SESSION_ID = "session_001"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_agent = Router(
    name="CustomRoutingAgent",
    route_agent=route_agent,
    travel_agent=travel_itinerary_agent,
    email_agent=email_writer_agent,
)


async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    logger.info(f"Session created: {session.id}")
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return session_service, runner


async def call_agent_async(user_input: str):
    session_service, runner = await setup_session_and_runner()

    content = types.Content(
        role="user",
        parts=[types.Part(text=user_input)],
    )
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content,
    )

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response:", final_response)

    final_session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    print("Final Session State:")
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")


if __name__ == "__main__":
    asyncio.run(call_agent_async("Plan a 3 day trip to Paris"))
