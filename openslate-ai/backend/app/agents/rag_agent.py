from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.planner_agent import route_question
from app.tools.rag_tool import rag_tool
from app.tools.web_tool import web_search_tool


class AgentState(TypedDict):
    question: str
    project_id: Optional[str]
    answer: Optional[str]
    sources: Optional[list]
    route: Optional[str]


def router_node(state: AgentState):
    return {
        "route": route_question(
            state["question"],
            state.get("project_id"),
        )
    }


def router_condition(state: AgentState):
    return state["route"]


def rag_node(state: AgentState):
    result = rag_tool(
        question=state["question"],
        project_id=state.get("project_id"),
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }


def web_node(state: AgentState):
    result = web_search_tool(
        question=state["question"],
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }


builder = StateGraph(AgentState)

builder.add_node("router_node", router_node)
builder.add_node("rag_node", rag_node)
builder.add_node("web_node", web_node)

builder.set_entry_point("router_node")

builder.add_conditional_edges(
    "router_node",
    router_condition,
    {
        "rag": "rag_node",
        "web": "web_node",
    },
)

builder.add_edge("rag_node", END)
builder.add_edge("web_node", END)

rag_agent = builder.compile()


def run_rag_agent(
    question: str,
    project_id: str | None = None,
):
    return rag_agent.invoke(
        {
            "question": question,
            "project_id": project_id,
            "answer": None,
            "sources": None,
            "route": None,
        }
    )