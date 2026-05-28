from dotenv import load_dotenv
from typing import Literal
import os
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


load_dotenv()

# -----------------------------
# STATE MODEL
# -----------------------------

class ProcessAgent(BaseModel):
    user_message: str
    sentiment: Literal["info", "action", "summary"] | None = None

parser = PydanticOutputParser(
    pydantic_object=ProcessAgent
)
# -----------------------------
# LLM
# -----------------------------
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=os.getenv(
        "HUGGINGFACEHUB_API_TOKEN"
    ),
    max_new_tokens=256,
    temperature=0.1,
)

# ---------------------------------------------------
# CHAT WRAPPER
# ---------------------------------------------------

chat_model = ChatHuggingFace(llm=llm)
# -------------------------------------------------
# PROMPT
# -------------------------------------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a classifier.

        Return valid JSON only.

        {format_instructions}
        """
    ),
    (
        "human",
        "{message}"
    )
])


# -------------------------------------------------
# CHAIN
# -------------------------------------------------

chain = (
    prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    | chat_model
    | parser
)

# -----------------------------
# NODE
# -----------------------------

def check_sentiment(state: dict):

    response = chain.invoke({
        "message": state["user_message"]
    })

    return {
        "user_message": response.user_message,
        "sentiment": response.sentiment
    }


# -------------------------------------------------
# GRAPH
# -------------------------------------------------

graph = StateGraph(dict)

graph.add_node("check_sentiment", check_sentiment)

graph.add_edge(START, "check_sentiment")
graph.add_edge("check_sentiment", END)

workflow = graph.compile()

# -------------------------------------------------
# RUN
# -------------------------------------------------

input_text = input("Enter your message: ")

result = workflow.invoke({
    "user_message": input_text
})

print("Result:", result)