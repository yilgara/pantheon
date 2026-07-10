"""Assemble the multi-agent graph.

Flow (mirrors TradingAgents, minus the Scanner which lives outside the graph):
  analysts (sequential) → Bull⇄Bear → Research Manager → Trader
  → Aggressive⇄Conservative⇄Neutral → Portfolio Manager → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from pantheon.agents import analysts as A
from pantheon.agents.managers import create_portfolio_manager, create_research_manager
from pantheon.agents.researchers import create_bear_researcher, create_bull_researcher
from pantheon.agents.risk import (
    create_aggressive_debator,
    create_conservative_debator,
    create_neutral_debator,
)
from pantheon.agents.tools import FUNDAMENTALS_TOOLS, MARKET_TOOLS, NEWS_TOOLS, SOCIAL_TOOLS
from pantheon.agents.trader import create_trader
from pantheon.graph.conditional import ConditionalLogic
from pantheon.graph.state import PantheonState

# (node name, factory, tools) — order defines the analyst sequence.
_ANALYSTS = [
    ("Market Analyst", A.create_market_analyst, MARKET_TOOLS),
    ("Social Media Analyst", A.create_social_analyst, SOCIAL_TOOLS),
    ("News Analyst", A.create_news_analyst, NEWS_TOOLS),
    ("Fundamentals Analyst", A.create_fundamentals_analyst, FUNDAMENTALS_TOOLS),
]
_RISK = ["Aggressive Analyst", "Conservative Analyst", "Neutral Analyst"]


def build_graph(quick_llm, deep_llm, config: dict):
    """Wire and compile the graph. quick_llm for analysts/debaters, deep_llm for judges."""
    A.set_quick_llm(quick_llm)
    logic = ConditionalLogic(config["max_debate_rounds"], config["max_risk_rounds"])
    g = StateGraph(PantheonState)

    # nodes
    for name, factory, _ in _ANALYSTS:
        g.add_node(name, factory())
    g.add_node("Bull Researcher", create_bull_researcher(quick_llm))
    g.add_node("Bear Researcher", create_bear_researcher(quick_llm))
    g.add_node("Research Manager", create_research_manager(deep_llm))
    g.add_node("Trader", create_trader(quick_llm))
    g.add_node("Aggressive Analyst", create_aggressive_debator(quick_llm))
    g.add_node("Conservative Analyst", create_conservative_debator(quick_llm))
    g.add_node("Neutral Analyst", create_neutral_debator(quick_llm))
    g.add_node("Portfolio Manager", create_portfolio_manager(deep_llm))

    # analyst chain
    g.add_edge(START, _ANALYSTS[0][0])
    for i, (name, _, _) in enumerate(_ANALYSTS):
        nxt = _ANALYSTS[i + 1][0] if i < len(_ANALYSTS) - 1 else "Bull Researcher"
        g.add_edge(name, nxt)

    # research debate (Bull⇄Bear → Research Manager)
    for dn in ("Bull Researcher", "Bear Researcher"):
        g.add_conditional_edges(dn, logic.research_router,
                                ["Bull Researcher", "Bear Researcher", "Research Manager"])
    g.add_edge("Research Manager", "Trader")

    # risk debate (Aggressive→Conservative→Neutral → Portfolio Manager)
    g.add_edge("Trader", "Aggressive Analyst")
    for rn in _RISK:
        g.add_conditional_edges(rn, logic.risk_router, _RISK + ["Portfolio Manager"])
    g.add_edge("Portfolio Manager", END)

    return g.compile()
