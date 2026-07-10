"""Run lifecycle: initial state → graph → (final_state, signal)."""

from __future__ import annotations

from typing import Any

from pantheon.agents.schemas import parse_rating
from pantheon.config import get_config
from pantheon.graph.build import build_graph
from pantheon.graph.state import new_research_debate, new_risk_debate


def create_initial_state(ticker: str, trade_date: str, selected_by: str = "human",
                         scanner_ranking: str = "") -> dict[str, Any]:
    return {
        "messages": [], "ticker": ticker, "trade_date": trade_date, "sender": "",
        "selected_by": selected_by, "scanner_ranking": scanner_ranking,
        "market_report": "", "sentiment_report": "", "news_report": "", "fundamentals_report": "",
        "research_debate": new_research_debate(), "investment_plan": "",
        "trade_proposal": "", "risk_debate": new_risk_debate(), "final_decision": "",
    }


def run_pipeline(ticker: str, trade_date: str, *, config: dict | None = None,
                 quick_llm=None, deep_llm=None):
    """Run a full analysis. Pass quick_llm/deep_llm to inject (e.g. a fake in tests);
    otherwise they are built from config via pantheon.llm."""
    cfg = config or get_config()
    if quick_llm is None or deep_llm is None:
        from pantheon.llm import get_deep_llm, get_quick_llm
        quick_llm = quick_llm or get_quick_llm(cfg)
        deep_llm = deep_llm or get_deep_llm(cfg)

    graph = build_graph(quick_llm, deep_llm, cfg)
    state = create_initial_state(ticker, trade_date, cfg.get("scanner_mode", "human"))
    final = graph.invoke(state, {"recursion_limit": cfg["max_recur_limit"]})
    return final, parse_rating(final["final_decision"])


# node name -> (UI team, short role, which state field carries its output)
_NODE_META = {
    "Market Analyst": ("analyst", "Analyzer · price & technicals", "market_report"),
    "Social Media Analyst": ("analyst", "Analyzer + Summarizer · sentiment", "sentiment_report"),
    "News Analyst": ("analyst", "Analyzer · news & macro", "news_report"),
    "Fundamentals Analyst": ("analyst", "Analyzer · fundamentals", "fundamentals_report"),
    "Bull Researcher": ("bull", "Judge · research debate", "research_debate"),
    "Bear Researcher": ("bear", "Judge · research debate", "research_debate"),
    "Research Manager": ("manager", "Judge + Instructor", "investment_plan"),
    "Trader": ("trader", "Recommender", "trade_proposal"),
    "Aggressive Analyst": ("risk-aggressive", "Judge · risk debate", "risk_debate"),
    "Conservative Analyst": ("risk-conservative", "Judge · risk debate", "risk_debate"),
    "Neutral Analyst": ("risk-neutral", "Judge · risk debate", "risk_debate"),
    "Portfolio Manager": ("pm", "Judge + Recommender", "final_decision"),
}
_RISK_KEY = {
    "Aggressive Analyst": "current_aggressive_response",
    "Conservative Analyst": "current_conservative_response",
    "Neutral Analyst": "current_neutral_response",
}


def _node_output(node: str, delta: dict) -> str:
    field = _NODE_META[node][2]
    if field == "research_debate":
        return delta["research_debate"]["current_response"].split(": ", 1)[-1]
    if field == "risk_debate":
        return delta["risk_debate"][_RISK_KEY[node]].split(": ", 1)[-1]
    return delta.get(field, "")


def stream_pipeline(ticker: str, trade_date: str, *, config: dict | None = None):
    """Generator yielding one event dict per agent as the graph runs.

    Each event: {agent, team, role, content}. The Portfolio Manager event also
    carries {decision: <rating>}. A final {done: True, signal} event closes it.
    """
    cfg = config or get_config()
    from pantheon.llm import get_deep_llm, get_quick_llm
    quick_llm, deep_llm = get_quick_llm(cfg), get_deep_llm(cfg)

    graph = build_graph(quick_llm, deep_llm, cfg)
    state = create_initial_state(ticker, trade_date, cfg.get("scanner_mode", "human"))

    signal = "Hold"
    for update in graph.stream(state, {"recursion_limit": cfg["max_recur_limit"]},
                               stream_mode="updates"):
        for node, delta in update.items():
            if node not in _NODE_META:
                continue
            team, role, _ = _NODE_META[node]
            content = _node_output(node, delta)
            event = {"agent": node, "team": team, "role": role, "content": content}
            if node == "Portfolio Manager":
                signal = parse_rating(delta.get("final_decision", ""))
                event["decision"] = signal
            yield event
    yield {"done": True, "signal": signal}
