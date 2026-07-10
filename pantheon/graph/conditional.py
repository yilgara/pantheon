"""Conditional routing for the two debate loops.

Both debates are fixed round-robins that terminate on a count threshold — no
content parsing, matching the reference approach.
"""

from __future__ import annotations


class ConditionalLogic:
    def __init__(self, max_debate_rounds: int = 1, max_risk_rounds: int = 1):
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_rounds = max_risk_rounds

    def research_router(self, state) -> str:
        d = state["research_debate"]
        if d["count"] >= 2 * self.max_debate_rounds:
            return "Research Manager"
        # alternate: whoever just spoke, the other goes next
        return "Bear Researcher" if d["current_response"].startswith("Bull") else "Bull Researcher"

    def risk_router(self, state) -> str:
        r = state["risk_debate"]
        if r["count"] >= 3 * self.max_risk_rounds:
            return "Portfolio Manager"
        last = r["latest_speaker"]
        if last == "Aggressive":
            return "Conservative Analyst"
        if last == "Conservative":
            return "Neutral Analyst"
        return "Aggressive Analyst"
