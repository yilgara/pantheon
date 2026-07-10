"""Analyst agents — the only agents that touch data (via tools).

All four share one factory; they differ by tool set, report key, and a short
role line. Each is a tool-loop node: it may call data tools (LangGraph routes
back to it with the results), and once it stops calling tools it writes its
report into the state.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from pantheon.agents.tools import FUNDAMENTALS_TOOLS, MARKET_TOOLS, NEWS_TOOLS, SOCIAL_TOOLS

_BASE = (
    "You are the {role} on an investment desk analyzing {ticker} as of {date}. "
    "Use the available tools to gather the data you need, then write a concise, "
    "decision-useful report (5-8 sentences). Focus on {focus}. State concrete "
    "figures where you have them and flag anything that cuts against the thesis. "
    "Do not give a final buy/sell call — that is decided later; your job is analysis."
)


def _make_analyst(name, role, focus, tools, report_key):
    def node(state) -> dict:
        system = _BASE.format(role=role, ticker=state["ticker"], date=state["trade_date"], focus=focus)
        # Seed the conversation on the first pass; afterwards the graph feeds
        # tool results back through state["messages"].
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system),
                        HumanMessage(content=f"Analyze {state['ticker']} as of {state['trade_date']}.")]

        llm_with_tools = _llm().bind_tools(tools)
        result = llm_with_tools.invoke(messages)

        # If the model wants tools, loop (report stays empty this pass).
        report = "" if getattr(result, "tool_calls", None) else result.content
        return {"messages": [result], report_key: report, "sender": name}

    return node


# quick model is set at wiring time; kept module-level for the factory closures.
_QUICK = None


def set_quick_llm(llm):
    global _QUICK
    _QUICK = llm


def _llm():
    if _QUICK is None:
        raise RuntimeError("analysts: call set_quick_llm(llm) before building the graph")
    return _QUICK


def create_market_analyst():
    return _make_analyst("Market Analyst", "market analyst",
                         "price action and technical indicators (trend, RSI, MACD, moving averages)",
                         MARKET_TOOLS, "market_report")


def create_social_analyst():
    return _make_analyst("Social Media Analyst", "social-media & sentiment analyst",
                         "crowd sentiment and narrative (bullish/bearish tone, notable shifts)",
                         SOCIAL_TOOLS, "sentiment_report")


def create_news_analyst():
    return _make_analyst("News Analyst", "news analyst",
                         "company and macro news, catalysts, and event risk",
                         NEWS_TOOLS, "news_report")


def create_fundamentals_analyst():
    return _make_analyst("Fundamentals Analyst", "fundamentals analyst",
                         "valuation, growth, margins, and balance-sheet health",
                         FUNDAMENTALS_TOOLS, "fundamentals_report")
