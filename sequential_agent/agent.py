from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.sequential_agent import SequentialAgent

LLM_MODEL = LiteLlm(model='azure/gpt-4o')

dsa_writer_agent = Agent(
    model=LLM_MODEL,
    name='CodingAgent',
    description='An agent which will write code for DSA problems',
    instruction='''
    You are an expert in Python Data Structure and Algorithms coding.
    You will be given a problem statement and you will need to write the code to solve the problem.
    You will need to use the best practices of Python programming to write the code.
    You will need to use the best practices of Data Structure and Algorithms to write the code.
    You will need to use the best practices of Python programming to write the code.
    *** OUTPUT FORMAT ***
    The entire code needs to be formatted as per Python syntax.
    The code should be enclosed in ```python tags.
    ''',
    output_key="code"
)


test_case_generator_agent = Agent(
    model=LLM_MODEL,
    name='TestCaseGeneratorAgent',
    description='An agent which will generate test cases for DSA problems',
    instruction="""
    You are an expert in generating test cases for DSA problems.
    You will analyze the generated code
    ```python
    {code}
    ```
    and generate test cases for the problem.
    You will need to use the best practices of generating test cases for DSA problems.
    You will need to generate test cases for the problem.
    You will need to use the best practices of generating test cases for DSA problems.
    """,
    output_key="test_cases"
)


final_agent = Agent(
    model=LLM_MODEL,
    name='FinalAgent',
    description='An agent which will combine the code and test cases to form a complete solution',
    instruction='''
    You are an expert in combining the code and test cases to form a complete solution.
    You will be given the code and test cases and you will need to combine them to form a complete solution.
    You will need to use the best practices of combining the code and test cases to form a complete solution.
    The solution and test files should be formatted into 2 different sections in the output.
    ''',
    output_key="solution"
)


# Create the sequential agent
root_agent = SequentialAgent(
    name="AssistantPilot",
    sub_agents=[dsa_writer_agent, test_case_generator_agent, final_agent],
    description="""Sequential agent which will write the code for DSA problems, 
    generate test cases for the code and combine the code and test cases to form a complete solution.""",
)