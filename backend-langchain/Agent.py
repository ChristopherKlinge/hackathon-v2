import config
from typing import List, Any
from tools import get_db_info, get_ambient, get_machine_data, get_logs
from dotenv import find_dotenv, load_dotenv
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage


load_dotenv(find_dotenv(), override=True)


class Agent:
    def __init__(self) -> None:
        # Define the LLM, that the Agent should use to talk to the User
        llm = ChatOpenAI(name=config.GPT_VERSION, temperature=config.TEMPERATURE)

        # Define the List of Tools, that the Agent should have Access to
        tools = [get_db_info, get_machine_data, get_ambient, get_logs]

        # Define the Prompt Template for the Agent --> nothing special here...
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", config.SYSTEM_PROMPT),
                ("placeholder", "{chat_history}"),
                ("user", "{user_prompt}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Define the Agent "Pipeline" itself --> Got simplified by the "create_tool_calling_agent" Function
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

        # Define the AgentExecutor Object that can be Invoked
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,  # set this to False to not dive into the mysterious thought processes of the AI ;)
        )

        self.conversation = []

    def reset_messages(self) -> None:
        self.conversation = []

    def create_chat_history(self) -> List[Any]:
        chat_hist = []
        for info in self.conversation:
            chat_hist.append(HumanMessage(content=info["user"]))
            chat_hist.append(AIMessage(content=info["bot"]))

        return chat_hist

    def get_response(
        self,
        prompt: str,
    ) -> str:
        """
        Small function just to wrap the process of building the prompt and invoking the AgentExecutor.

        Args:
            prompt (str): New prompt asked by the user

        Returns:
            str: Answer from the agent
        """

        timestamp_prompt_part = (
            f"\n\nTimestamp: {datetime.now().strftime(config.DATETIME_FORMAT)}"
        )
        chat_hist = self.create_chat_history()
        resp = self.agent_executor.invoke(
            {"user_prompt": prompt + timestamp_prompt_part, "chat_history": chat_hist}
        )["output"]
        self.conversation.append({"user": prompt, "bot": resp})

        return resp
