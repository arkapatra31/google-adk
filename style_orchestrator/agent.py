from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from style_orchestrator.image_suggester import suggest_image, take_pending_images

LLM_MODEL = LiteLlm(model="azure/gpt-4o")


def set_query(callback_context: CallbackContext):
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        callback_context.state["user_query"] = user_content.parts[0].text


def attach_images(callback_context: CallbackContext) -> types.Content | None:
    """Append suggested images as markdown data-URIs so the web UI renders them."""
    images = take_pending_images()
    if not images:
        return None

    model_output = callback_context.state.get("output", "")
    lines = [str(model_output)] if model_output else []

    for img in images:
        data_uri = f"data:{img['mime_type']};base64,{img['data']}"
        lines.append(f"\n\n![{img.get('desc', img['name'])}]({data_uri})\n\n")

    return types.Content(
        role="model",
        parts=[types.Part.from_text(text="\n".join(lines))],
    )


root_agent = LlmAgent(
    model=LLM_MODEL,
    name="style_orchestrator",
    description="An agent which can suggest images to the user based on the user query.",
    instruction="""
    You will have the user query in {{user_query}}.
    Use the suggest_image tool to find relevant images for the user.
    Summarise the results you get back from the tool in a helpful way.
    """,
    before_agent_callback=set_query,
    after_agent_callback=attach_images,
    output_key="output",
    tools=[suggest_image],
)
