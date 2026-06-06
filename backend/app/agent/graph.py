from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from backend.app.agent.prompts import SYSTEM_PROMPT, DOC_GENERATION_PROMPT
from backend.app.config import settings
import json
import re
import logging

logger = logging.getLogger(__name__)


class DocState(TypedDict):
    code: str
    language: str
    function_name: str
    raw_response: Optional[str]
    parsed_doc: Optional[dict]
    formatted_markdown: Optional[str]
    error: Optional[str]
    retry_count: int


def call_llm(state: DocState) -> DocState:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.gemini_api_key,
        temperature=0,
    )
    prompt = DOC_GENERATION_PROMPT.format(
        language=state["language"],
        code=state["code"],
    )
    try:
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
        return {**state, "raw_response": response.content, "error": None}
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return {**state, "error": str(e)}


def parse_response(state: DocState) -> DocState:
    if state.get("error") or not state.get("raw_response"):
        return state
    try:
        raw = state["raw_response"].strip()

        # Bug #2 fix — robust markdown stripping with regex
        code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(code_block_pattern, raw, re.IGNORECASE)
        if match:
            raw = match.group(1)

        parsed = json.loads(raw.strip())
        return {**state, "parsed_doc": parsed}
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e}\nRaw response: {raw[:200]}")
        return {**state, "error": str(e), "retry_count": state["retry_count"] + 1}


def format_markdown(state: DocState) -> DocState:
    if not state.get("parsed_doc"):
        return state
    doc = state["parsed_doc"]
    fn = state["function_name"]
    lines = [
        f"### `{fn}`",
        "",
        doc.get("summary", ""),
        "",
        doc.get("description", ""),
    ]
    if doc.get("parameters"):
        lines += ["", "**Parameters**"]
        # Bug #3 fix — use .get() with defaults
        for p in doc.get("parameters", []):
            name = p.get("name", "unknown")
            type_ = p.get("type", "any")
            desc = p.get("description", "No description")
            lines.append(f"- `{name}` *({type_})*: {desc}")
    if doc.get("returns") and doc["returns"].get("description"):
        r = doc["returns"]
        lines += ["", f"**Returns** `{r.get('type', 'unknown')}`: {r['description']}"]
    if doc.get("raises"):
        lines += ["", "**Raises**"]
        for exc in doc.get("raises", []):
            exc_name = exc.get("exception", "Exception")
            condition = exc.get("condition", "")
            lines.append(f"- `{exc_name}`: {condition}")
    if doc.get("warnings"):
        lines += ["", "**Warnings**"]
        for w in doc.get("warnings", []):
            lines.append(f"- {w}")
    if doc.get("complexity"):
        lines += ["", f"*Complexity: {doc['complexity']}*"]
    return {**state, "formatted_markdown": "\n".join(lines)}


def should_retry(state: DocState) -> str:
    error = str(state.get("error", "")).lower()
    non_retryable = ["authentication", "401", "credit", "billing", "400", "invalid", "api error"]
    if state.get("error"):
        if any(keyword in error for keyword in non_retryable):
            return "end"
        if state.get("retry_count", 0) < 2:
            return "retry"
    return "end"


def build_doc_graph():
    graph = StateGraph(DocState)
    graph.add_node("call_llm", call_llm)
    graph.add_node("parse_response", parse_response)
    graph.add_node("format_markdown", format_markdown)
    graph.set_entry_point("call_llm")
    graph.add_edge("call_llm", "parse_response")
    graph.add_conditional_edges(
        "parse_response",
        should_retry,
        {
            "retry": "call_llm",
            "end": "format_markdown",
        },
    )
    graph.add_edge("format_markdown", END)
    return graph.compile()


doc_agent = build_doc_graph()


def generate_documentation(code: str, function_name: str, language: str) -> str:
    initial_state = DocState(
        code=code,
        language=language,
        function_name=function_name,
        raw_response=None,
        parsed_doc=None,
        formatted_markdown=None,
        error=None,
        retry_count=0,
    )
    result = doc_agent.invoke(initial_state)

    # Bug #4 fix — informative fallback message
    if result.get("error") or not result.get("formatted_markdown"):
        error_msg = result.get("error", "Unknown error")
        logger.error(f"Documentation generation failed for {function_name}: {error_msg}")
        return (
            f"### `{function_name}`\n\n"
            f"*Documentation generation failed. "
            f"Save the file again to retry.*"
        )
    return result["formatted_markdown"]
