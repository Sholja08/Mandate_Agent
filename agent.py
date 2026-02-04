import json
import uuid
import datetime
import asyncio
import inspect
from typing import Any

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, AIMessage, SystemMessage, HumanMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from mandate_agent.prompts import SYSTEM_PROMPT, HUMAN_PROMPT
from mandate_agent.schema import AgentDecision
from mandate_agent.mcp_client import load_mcp_tools   # ✅ MCP ONLY


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOAD MCP TOOLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MANDATE_TOOLS = load_mcp_tools()   # {name: StructuredTool}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AgentState(BaseModel):
    messages: list[Any] = Field(default_factory=list)
    last_decision: AgentDecision | None = None
    current_mandate: str | None = None
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FORMATTERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _format_mandate(m: dict) -> str:
    icon = "✅" if m["status"] == "unpaused" else "⏸️" if m["status"] == "pause" else "❌"
    return f"""
{icon} {m['mandate_name']}
Mandate ID: {m.get('mandate_id', 'N/A')}
Bank: {m['bank']}
Amount: ₹{m['amount']}
Status: {m['status']}
Execution: {m['execution_frequency']} | {m['execution_date']}
Phone: {m['phone_no']}
"""


def format_tool_result(data: dict) -> str:

    if "error" in data:
        return f"❌ {data['error']}"

    # ✅ SHOW ALL MANDATES (NAMES ONLY)
    if "mandates" in data:
        if not data["mandates"]:
            return "📋 You don't have any mandates."

        lines = ["📋 Your Mandates:\n" + "─" * 40]
        for i, m in enumerate(data["mandates"], 1):
            icon = "✅" if m["status"] == "unpaused" else "⏸️" if m["status"] == "pause" else "❌"
            lines.append(f"{i}. {icon} {m['mandate_name']}  ({m.get('mandate_id','')})")

        return "\n".join(lines)

    # ✅ DETAILS
    if "matches" in data:
        if not data["matches"]:
            return "❌ No mandates found."
        
        lines = ["📄 Mandate Details:\n" + "─" * 50]
        for m in data["matches"]:
            lines.append(_format_mandate(m))
        return "\n".join(lines)

    # ✅ UPDATE ACTIONS
    if "success" in data and "updated_mandates" in data:
        lines = ["✅ Mandate updated successfully!\n" + "─" * 50]
        for m in data["updated_mandates"]:
            lines.append(_format_mandate(m))
        return "\n".join(lines)

    if "success" in data:
        return "✅ Action completed successfully."

    return json.dumps(data, indent=2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_mandate_agent(llm: ChatOpenAI):

    llm_json = llm.bind(response_format={"type": "json_object"})

    # -------------------------------
    # PROCESS NODE
    # -------------------------------
    def process_node(state: AgentState):

        user_msg = state.messages[-1].content

        history = "\n".join(
            f"{type(m).__name__}: {m.content}" for m in state.messages[:-1]
        ) or "No previous conversation"

        system_msg = SYSTEM_PROMPT.format(
            current_date=str(datetime.datetime.now()),
            available_tools=", ".join(MANDATE_TOOLS.keys()),
            current_mandate=state.current_mandate or "None",
            chat_history=history
        )

        try:
            response = llm_json.invoke([
                SystemMessage(content=system_msg),
                HumanMessage(content=HUMAN_PROMPT.format(user_input=user_msg))
            ])

            state.last_decision = AgentDecision(**json.loads(response.content))
        except Exception as e:
            state.last_decision = AgentDecision(
                intent="ERROR",
                thought=str(e),
                action="output",
                action_input={"message": "I couldn't understand that. Please rephrase."}
            )

        return state


    # -------------------------------
    # TOOL NODE (ASYNC MCP)
    # -------------------------------
    async def tool_node(state: AgentState):

        decision = state.last_decision

        if decision.action not in MANDATE_TOOLS:
            return state

        tool = MANDATE_TOOLS[decision.action]
        raw_args = decision.action_input or {}

        # map mandate_name -> query
        if "mandate_name" in raw_args and "query" not in raw_args:
            raw_args["query"] = raw_args.pop("mandate_name")

        try:
            result = await tool.ainvoke(raw_args)
        except Exception as e:
            result = {"error": f"MCP tool error: {str(e)}"}

        state.messages.append(
            ToolMessage(content=json.dumps(result), tool_call_id=str(uuid.uuid4()))
        )

        return state


    # -------------------------------
    # OUTPUT NODE
    # -------------------------------
    def output_node(state: AgentState):

        # If LLM chose to directly speak
        if state.last_decision and state.last_decision.action == "output":
            msg = state.last_decision.action_input.get("message", "How can I help you?")
            state.messages.append(AIMessage(content=msg))
            return state

        tool_msgs = [m for m in state.messages if isinstance(m, ToolMessage)]

        if tool_msgs:
            try:
                raw_content = json.loads(tool_msgs[-1].content)

                # ✅ MCP always returns list of blocks
                if isinstance(raw_content, list) and raw_content:
                    block = raw_content[0]
                    if isinstance(block, dict) and "text" in block:
                        data = json.loads(block["text"])   # ✅ REAL tool JSON
                    else:
                        data = raw_content
                else:
                    data = raw_content

                text = format_tool_result(data)

            except Exception as e:
                text = f"❌ Error formatting MCP response: {str(e)}"
        else:
            text = "How can I assist you with your UPI mandates?"

        state.messages.append(AIMessage(content=text))
        return state


    # -------------------------------
    # ROUTER
    # -------------------------------
    def router(state: AgentState):
        if not state.last_decision:
            return "output"

        if state.last_decision.action in MANDATE_TOOLS:
            return "tool"

        return "output"


    # -------------------------------
    # GRAPH
    # -------------------------------
    graph = StateGraph(AgentState)

    graph.add_node("process", process_node)
    graph.add_node("tool", tool_node)
    graph.add_node("output", output_node)

    graph.add_edge(START, "process")

    graph.add_conditional_edges("process", router, {
        "tool": "tool",
        "output": "output"
    })

    graph.add_edge("tool", "output")
    graph.add_edge("output", END)

    return graph.compile()

from langchain_core.messages import HumanMessage

async def run_mandate_agent(user_query: str, llm, mandate_state: dict | None = None):

    if not mandate_state:
        agent = get_mandate_agent(llm)
        mandate_state = {"agent": agent, "messages": []}
    else:
        agent = mandate_state["agent"]

    mandate_state["messages"].append(HumanMessage(content=user_query))

    # ❗ MUST BE ainvoke
    result = await agent.ainvoke({"messages": mandate_state["messages"]})

    mandate_state["messages"] = result.get("messages", mandate_state["messages"])

    messages = mandate_state["messages"]
    if messages:
        return messages[-1].content, mandate_state

    return "I couldn't process your mandate request.", mandate_state
