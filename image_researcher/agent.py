import base64
import json
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from .output_schema import ImageAnalysisResponse

# IMAGE_LLM = LiteLlm(model="ollama/gemma3:latest")
IMAGE_LLM = LiteLlm(model="azure/gpt-4o")


def analyze_input(callback_context: CallbackContext):
    """Extract image from user input, encode to base64, and store in session state."""
    user_content = callback_context.user_content
    print(f"[User Content] \n {user_content}")
    if not user_content or not user_content.parts:
        return

    for part in user_content.parts:
        # Extract the user question (only when part has non-empty text; image parts have text=None)
        part_text = getattr(part, "text", None)
        if part_text and part_text.strip():
            callback_context.state["user_question"] = part_text.strip()
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            image_b64 = convert_img_to_b64(part.inline_data.data)
            callback_context.state["image_base64"] = image_b64
            callback_context.state["image_mime_type"] = getattr(
                part.inline_data, "mime_type", "image/png"
            )


def convert_img_to_b64(image_bytes: bytes) -> str:
    """Convert raw image bytes to a base64-encoded string using the base64 library."""
    return base64.b64encode(image_bytes).decode("utf-8")


INCLUDE_FIELDS = ["extracted_data", "structured_data"]


def filter_response(callback_context: CallbackContext) -> types.Content | None:
    """Strip output fields not listed in INCLUDE_FIELDS."""
    raw = callback_context.state.get("output")
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        filtered = {k: v for k, v in data.items() if k in INCLUDE_FIELDS}
        return types.Content(
            role="model",
            parts=[types.Part.from_text(text=json.dumps(filtered, indent=2))],
        )
    except (json.JSONDecodeError, AttributeError):
        return None


root_agent = Agent(
    model=IMAGE_LLM,
    name="image_researcher",
    description="An image analysis assistant powered by Azure GPT-4o",
    instruction="""
        You have to analyze and answer to user question with respect to user question.
        You will have the base64 encoded image in {{image_base64}} and the
        user query in {{user_question}}.
        After analyzing the image and the question carefully answer the question.
        *** OUTPUT FORMAT ***
        The output should follow the output schema provided to the agent.
        Rules:- 
            1. Be short and precise
            2. Stick to the user's question for relevance.
            3. You are only allowed to call tools if provided.
    """,
    before_agent_callback=analyze_input,
    output_schema=ImageAnalysisResponse,
    output_key="output",
    after_agent_callback=filter_response,
)
