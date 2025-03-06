# For UI and Panda
import streamlit as st
import pandas as pd
import time
# For LLM
from langchain_community.chat_models import AzureChatOpenAI

# For agent
from langchain.agents import AgentType
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# For API and environment setup
import os
import prompt

if "messages" not in st.session_state:
    st.session_state.messages = []

# REPL tool
tools = [PythonREPLTool()]

from dotenv import load_dotenv
load_dotenv()
# Retrieve Azure OpenAI specific configuration from environment variables
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE")
OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize an instance of AzureChatOpenAI using the specified settings
chat_llm = AzureChatOpenAI(
    openai_api_version=OPENAI_API_VERSION,
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    deployment_name="Siddhi4om"
)

st.set_page_config(layout="wide")
st.title("Sheets Navigator")
files = st.file_uploader("upload csv file", type=["csv"], accept_multiple_files=False)

if files is not None:
    df = pd.read_csv(files)

    agent = create_pandas_dataframe_agent(
        llm=chat_llm,
        df=df,
        prefix=prompt.prefix_prmt,
        suffix=prompt.sufix,
        include_df_in_prompt=False,
        verbose=True,
        extra_tools=tools,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
    )

    placeholder = st.empty()
    with placeholder:
        st.info("File upload successful")
        time.sleep(1.5)
        placeholder.empty()

    st.write(df.head(3))

    query = st.chat_input("Enter query")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if query:
        with st.chat_message("user"):
            st.markdown(query)
            st.session_state.messages.append({"role": "user", "content": query})

        resp = agent.invoke(query)
        response = resp["output"].replace("*", "").replace("#", "").replace("`", "")
        st.write(response)
        print(response)

    with st.chat_message("assistant"):
        st.session_state.messages.append({"role": "assistant", "content":response})
        st.write(response)
        if os.listdir("chart") is not None:
            for filename in os.listdir("chart"):
                f = os.path.join("chart", filename)
                # checking if it is a file
                if os.path.isfile(f):
                    st.image(f, width=500)
