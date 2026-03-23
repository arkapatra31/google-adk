from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent


LLM_MODEL = LiteLlm(model='azure/gpt-4o')

# Research Agent 1
concise_research_agent_1 = LlmAgent(
    model=LLM_MODEL,
    name='research_agent_1',
    description='A helpful concise research agent which will research the user question.',
    instruction='''
    You will research the user question and provide the information to the user.
    The information should be concise and to the point.
    ''',
    output_key='concise_research_1',
)

# Research Agent 2
detailed_research_agent_2 = LlmAgent(
    model=LLM_MODEL,
    name='research_agent_2',
    description='A helpful detailed research agent which will research the user question.',
    instruction='''
    You will research the user question and provide the information to the user.
    The information should be detailed and to the point.
    ''',
    output_key='detailed_research_2',
)

# Create the parallel agent
parallel_agent = ParallelAgent(
    name='parallel_agent',
    sub_agents=[concise_research_agent_1, detailed_research_agent_2],
    description='''A parallel agent which will research the user question and provide 
    the information to the user.
    The information should be concise and to the point.''',
)

# Create a merger agent that will merge the information from the 
# two research agents and provide the final information to the user.
merger_agent = LlmAgent(
    model=LLM_MODEL,
    name='merger_agent',
    description='A helpful merger agent which will merge the information from the two research agents and provide the final information to the user.',
    instruction='''
    You will analyze the research results from the following reports :
    Concise Research Report : {{concise_research_1}}
    Detailed Research Report : {{detailed_research_2}}
    Your job is to analyze and merge and provide the best results
    ''',
    output_key='final_information',
)

# Create the pipeline that will use the parallel agent and the merger agent
root_agent = SequentialAgent(
    name='root_agent',
    sub_agents=[parallel_agent, merger_agent],
    description='''A sequential agent which will use the parallel agent and the merger agent to 
    research the user question and provide the final information to the user.''',
)