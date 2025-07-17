from __future__ import annotations

"""LangChain-based planner for converting instructions into action plans."""

import logging
from typing import List

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

_PROMPT = PromptTemplate(
    input_variables=["command"],
    template="Generate a numbered list of steps to accomplish: {command}",
)


def plan(command: str) -> List[str]:
    """Return a list of action steps for ``command``."""
    llm = ChatOpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=_PROMPT)
    result = chain.predict(command=command)
    return [line.strip("- ") for line in result.splitlines() if line.strip()]


__all__ = ["plan"]
