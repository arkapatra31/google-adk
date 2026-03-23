import logging
from typing import AsyncGenerator

from typing_extensions import override
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Router(BaseAgent):
    """
    A custom agent that routes the user request to the appropriate sub-agent.

    The route_agent (LLM) classifies the request and writes its decision to
    session state via output_key="agent_name". This agent then reads that
    state value and delegates to the matching sub-agent.

    Sub-agents:
      1. TravelItineraryAgent - handles travel-related queries
      2. EmailWriterAgent     - handles email-writing queries
    """

    route_agent: LlmAgent
    travel_agent: LlmAgent
    email_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        route_agent: LlmAgent,
        travel_agent: LlmAgent,
        email_agent: LlmAgent,
    ):
        super().__init__(
            name=name,
            route_agent=route_agent,
            travel_agent=travel_agent,
            email_agent=email_agent,
            sub_agents=[route_agent, travel_agent, email_agent],
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] Routing user request...")

        async for event in self.route_agent.run_async(ctx):
            logger.info(f"[{self.name}] Route agent event: {event.author}")
            yield event

        route_decision = ctx.session.state.get("agent_name", "")
        logger.info(f"[{self.name}] Route decision: {route_decision}")

        if "TravelItineraryAgent" in route_decision:
            logger.info(f"[{self.name}] Delegating to TravelItineraryAgent")
            async for event in self.travel_agent.run_async(ctx):
                yield event
        elif "EmailWriterAgent" in route_decision:
            logger.info(f"[{self.name}] Delegating to EmailWriterAgent")
            async for event in self.email_agent.run_async(ctx):
                yield event
        elif "Both" in route_decision:
            logger.info(f"[{self.name}] Delegating to both TravelItineraryAgent and EmailWriterAgent")
            async for event in self.travel_agent.run_async(ctx):
                yield event
            async for event in self.email_agent.run_async(ctx):
                yield event
        else:
            logger.warning(
                f"[{self.name}] Unknown route '{route_decision}', defaulting to TravelItineraryAgent"
            )
            # Prepare a custom Event with the message "Agent is not designed to handle this request"
            event = Event(
                author="RouterAgent",
                content=types.Content(
                    role="user",
                    parts=[types.Part(text="Agent is not designed to handle this request")],
                ),
            )
            yield event

        logger.info(f"[{self.name}] Routing complete.")
