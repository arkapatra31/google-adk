from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os

load_dotenv()

# Route Agent
route_agent = LlmAgent(
    model=LiteLlm(model=os.getenv("AZURE_LLM_MODEL")),
    name="RouteAgent",
    description="A agent that routes the user request to the appropriate sub-agent.",
    instruction="""
    You are a route agent.
    You will be given a user request and you will need to analyze the request and determine
    if the request is related to travel or email.
    If the request is related to travel, you will need to route the request to the TravelItineraryAgent.
    If the request is related to email, you will need to route the request to the EmailWriterAgent.
    If the request is related to both, you will need to route the request to 
        both the TravelItineraryAgent and the EmailWriterAgent.
    If the request is not related to travel or email, you will need respond with "Unknown".

    *** OUTPUT FORMAT ***
    The output should be in the following format:
    "TravelItineraryAgent" | "EmailWriterAgent" | "Both" | "Unknown"
    """,
    output_key="agent_name",
)

# Travel Itinerary Agent
travel_itinerary_agent = LlmAgent(
    model=LiteLlm(model=os.getenv("AZURE_LLM_MODEL")),
    name="TravelItineraryAgent",
    description="A agent that generates a travel itinerary based on the user request.",
    instruction="""
    You are a travel itinerary agent.
    You will be given a user request and you will need to generate a travel itinerary based on the user request.
    """,
    output_key="travel_itinerary",
)


# Email Writer Agent
email_writer_agent = LlmAgent(
    model=LiteLlm(model=os.getenv("AZURE_LLM_MODEL")),
    name="EmailWriterAgent",
    description="A agent that writes an email based on the user request.",
    instruction="""
    You are a email writer agent.
    You will be given a user request and you will need to write an email based on the user request.
    """,
    output_key="email",
)

__all__ = [
    "route_agent",
    "travel_itinerary_agent",
    "email_writer_agent",
]
