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
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
load_dotenv()

class ProcessAgent(BaseModel):
    user_message: str
    sentiment: Literal["info", "action", "summary"] | None = None

parser = PydanticOutputParser(pydantic_object=ProcessAgent)
# -----------------------------
# LLM
# -----------------------------
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")


llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.3-70B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=hf_token,
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
    SystemMessagePromptTemplate.from_template(
        "You are a classifier. Return valid JSON only.\n{format_instructions}"
    ),
    HumanMessagePromptTemplate.from_template("{message}")
]).partial(format_instructions=parser.get_format_instructions())

# -------------------------------------------------
# CHAIN
# -------------------------------------------------

chain = prompt | chat_model  | parser


# -------------------------------------------------
# RUN
# -------------------------------------------------
input_text = input("Enter your message: ")

result = chain.invoke({
    "message": input_text
})

print("Sentiment:", result.sentiment)
