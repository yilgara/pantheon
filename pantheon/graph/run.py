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
