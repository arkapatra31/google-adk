from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm


def response_formatter(response):
    """
    Format the response from the model to a more readable format with emojis

    Returns:
        str: The formatted response with emojis
    """
    return "🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻🧑‍💻"+response

root_agent = Agent(
    model=LiteLlm(model='azure/gpt-4o'),
    name='QnA_Agent',
    description='A helpful assistant for user questions and answers.',
    instruction='''
    Answer user questions and answers to the best of your knowledge.
    Use the tool provided to format the response in a more readable format with emojis.
    ''',
    tools=[response_formatter]
)
