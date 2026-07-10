"""Shared graph state.

A flat TypedDict extending LangGraph's MessagesState. Analyst outputs are prose
reports; debates are concatenated-string transcripts with a `count` that drives
termination (no content parsing). Pantheon adds `selected_by` / `scanner_ranking`
for the Equity Scanner.
"""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import MessagesState


class ResearchDebate(TypedDict):
    bull_history: str
    bear_history: str
    history: str            # combined transcript
    current_response: str   # last speaker's turn (used to alternate)
    judge_decision: str     # Research Manager's plan
    count: int              # incremented each Bull/Bear turn


class RiskDebate(TypedDict):
    aggressive_history: str
    conservative_history: str
    neutral_history: str
    history: str
    latest_speaker: str     # "Aggressive" | "Conservative" | "Neutral"
    current_aggressive_response: str
    current_conservative_response: str
    current_neutral_response: str
    judge_decision: str     # Portfolio Manager's final decision
    count: int              # incremented each risk turn


class PantheonState(MessagesState):
    # scalars
    ticker: str
    trade_date: str
    sender: str

    # Pantheon addition — the Equity Scanner
    selected_by: str        # "human" | "scanner"
    scanner_ranking: str     # markdown table when scanner mode, else ""

    # analyst reports (prose)
    market_report: str
    sentiment_report: str
    news_report: str
    fundamentals_report: str

    # research debate → plan
    research_debate: ResearchDebate
    investment_plan: str

    # execution
    trade_proposal: str

    # risk debate → final
    risk_debate: RiskDebate
    final_decision: str


def new_research_debate() -> ResearchDebate:
    return ResearchDebate(
        bull_history="", bear_history="", history="",
        current_response="", judge_decision="", count=0,
    )


def new_risk_debate() -> RiskDebate:
    return RiskDebate(
        aggressive_history="", conservative_history="", neutral_history="",
        history="", latest_speaker="",
        current_aggressive_response="", current_conservative_response="",
        current_neutral_response="", judge_decision="", count=0,
    )
