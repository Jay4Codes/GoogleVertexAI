from dotenv import load_dotenv
import os
import re
import datetime as dt
from langchain.chat_models import ChatOpenAI
from langchain.llms import VertexAI
from langchain.tools import Tool
import client_calendar as cc
import client_gmail as cg
import datetime as dt
import streamlit as st

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.agents import LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain import LLMChain
from langchain.utilities import SerpAPIWrapper
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish
from dotenv import dotenv_values
import gcloud_services as gs
import streamlit as st


load_dotenv()


def init_llm_and_serpapi():
    # llm = ChatOpenAI(
    #     model="gpt-3.5-turbo",
    #     temperature=0,
    #     openai_api_key=config["OPENAI_API_KEY"],
    # )

    # ["project", "location", "credentials"]
    llm = VertexAI(max_output_tokens=1024)

    search = SerpAPIWrapper(
        params={
            "engine": "google",
            "location": "Mumbai, Maharashtra, India",
        },
        serpapi_api_key=os.getenv("SERPAPI_API_KEY"),
    )

    return llm, search


def init_tools(search):

    def book_appointment(input_text):

        business_name = re.search(
            r"business_name: (.+?),", input_text).group(1).title()
        customer_name = re.search(
            r"customer_name: (.+?),", input_text).group(1).title()
        datetime = re.search(r"datetime: (.+?),", input_text).group(1).title()
        purpose = re.search(r"purpose: (.+?)$", input_text).group(1).title()

        if business_name == "[business_name]" or business_name == "[user_name]":
            return "Business Name not provided."
        if customer_name == "[customer_name]" or customer_name == "[user_name]":
            return "Customer Name not provided."
        if datetime == "[datetime]":
            return "Date and/or Time not provided."
        if purpose == "[purpose]":
            return "Purpose not provided."

        try:
            datetime = dt.datetime.strptime(datetime, "%Y-%m-%d %H:%M:%S")
        except:
            return "Ask the user to provide both the date and time for the appointment."

        if datetime < dt.datetime.now():
            return "Datetime provided is in the past. Please provide a future date and time."

        start_datetime = datetime.strftime("%Y-%m-%dT%H:%M:%S")
        end_datetime = datetime + dt.timedelta(hours=1)

        end_datetime = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

        print(f"Business Name: {business_name}")
        print(f"Customer Name: {customer_name}")
        print(f"Date and Time: {datetime}")
        print(f"Purpose: {purpose}")
        # TODO: Perform API Call to book appointment

        user_service, calendar_service, mail_service = gs.get_services()
        cc.create_event(calendar_service, summary=business_name, description=purpose, startDateTime=start_datetime,
                        endDateTime=end_datetime, timeZone="Asia/Kolkata", location="Mumbai, Maharashtra, India")

        cg.send_gmail(user_service, mail_service, receiver="arihant.sheth0802@gmail.com",
                      description=f"{purpose} confirmed at {business_name}", startDateTime=start_datetime, endDateTime=end_datetime, location="Mumbai, Maharashtra, India", subject=f"Appointment Confirmed at {business_name}", summary=f"{purpose} at {business_name}")
        st.balloons()

        return f"{customer_name}'s {purpose} reservation booked with {business_name} at {datetime}. Event has been created in user's calendar and an email has been sent to the user."

    def ask_within_context(input_text):
        return "You can answer this question yourself. Use your own knowledge or conversation history to answer the question."

    tools = [
        Tool(
            name="Book appointment",
            func=book_appointment,
            description=f"Useful only when user details are inputted by the user wants to book the appointment. Do not make up any parameter. Current datetime: {dt.datetime.now()}Pass the customer name, business name, datetime (in %Y-%m-%d %H:%M:%S format), and purpose of the appointment in the following format. Format: customer_name: [customer_name], business_name: [business_name], datetime: [datetime], purpose: [purpose] \nParameter Missing Example: customer_name: [customer_name], business_name: [business_name], datetime: [datetime], purpose: [purpose] \nBoth date and time should be present, else datetime: [datetime].",
        ),
        Tool(
            name="Search",
            description="Useful when user asks about restaurants, hotels, or other businesses. Give detailed response about the ratings, price range and websites about the businesses. Also include reviews from Google Reviews. Location: Mumbai, India.",
            func=search.run,
        ),
        Tool(
            name="No action required",
            description="No action required. Use your own knowledge or conversation history to answer the question.",
            func=ask_within_context,
        )
    ]

    return tools


def init_agent(llm, tools):

    template_with_history = """\
You are a compassionate, talkative AI Receptionist, named Linus. You have to help users with their bookings. 
Ask the user if they require any help. All queries are related to Mumbai, India. 
When the user asks you to suggest some good restaurants, hotels, or other businesses, use the Search tool to find the best businesses. Also include reviews from Google Reviews, their price range, and what they are famous for.
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. format your answer in a detailed way and give long answers.

Begin! Remember to answer as a compansionate AI Receptionist when giving your final answer.

Previous conversation history:
{history}

Question: {input}
{agent_scratchpad}"""

    class CustomPromptTemplate(StringPromptTemplate):
        # The template to use
        template: str
        # The list of tools available
        tools: List[Tool]

        def format(self, **kwargs) -> str:
            # Get the intermediate steps (AgentAction, Observation tuples)
            # Format them in a particular way
            intermediate_steps = kwargs.pop("intermediate_steps")
            thoughts = ""
            for action, observation in intermediate_steps:
                thoughts += action.log
                thoughts += f"\nObservation: {observation}\nThought: "
            # Set the agent_scratchpad variable to that value
            kwargs["agent_scratchpad"] = thoughts
            # Create a tools variable from the list of tools provided
            kwargs["tools"] = "\n".join(
                [f"{tool.name}: {tool.description}" for tool in self.tools])
            # Create a list of tool names for the tools provided
            kwargs["tool_names"] = ", ".join(
                [tool.name for tool in self.tools])
            return self.template.format(**kwargs)

    prompt_with_history = CustomPromptTemplate(
        template=template_with_history,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps", "history"]
    )

    class CustomOutputParser(AgentOutputParser):

        def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
            # Check if agent should finish
            if "Final Answer:" in llm_output:
                return AgentFinish(
                    # Return values is generally always a dictionary with a single `output` key
                    # It is not recommended to try anything else at the moment :)
                    return_values={"output": llm_output.split(
                        "Final Answer:")[-1].strip()},
                    log=llm_output,
                )
            # Parse out the action and action input
            regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
            match = re.search(regex, llm_output, re.DOTALL)
            if not match:
                print(f"\n\n\n\n\n{llm_output}\n\n\n\n\n")
                raise ValueError(f"Could not parse LLM output: `{llm_output}`")
            action = match.group(1).strip()
            action_input = match.group(2)
            # Return the action and action input
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

    output_parser = CustomOutputParser()

    llm_chain = LLMChain(llm=llm, prompt=prompt_with_history)

    tool_names = [tool.name for tool in tools]

    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    memory = ConversationBufferWindowMemory(k=5)

    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory
    )

    return agent_executor


def execute_agent(agent_executor, query):
    return agent_executor.run(query)

@st.experimental_singleton
def init_llm():
    print("Initializing LLM")
    llm, search = init_llm_and_serpapi()
    print("Initializing Agent")
    tools = init_tools(search)
    agent_executor = init_agent(llm, tools)

    return agent_executor

    # to execute the agent, call execute_agent with the query
    # execute_agent(agent_executor, query)
