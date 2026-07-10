"""Structured outputs for the decision-making agents.

Pydantic models + `render_*` functions that turn them into the markdown the
rest of the system (state, UI, trace) reads. A small `parse_rating` extracts
the headline signal from the final decision.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field


class PortfolioRating(str, Enum):
    BUY = "Buy"
    OVERWEIGHT = "Overweight"
    HOLD = "Hold"
    UNDERWEIGHT = "Underweight"
    SELL = "Sell"


class TraderAction(str, Enum):
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"


# Conviction tier -> nominal portfolio weight (Pantheon has no real benchmark,
# so the 5-point scale maps directly to target position size).
RATING_WEIGHTS: dict[str, float] = {
    "Buy": 8.0, "Overweight": 5.0, "Hold": 3.0, "Underweight": 1.0, "Sell": 0.0,
}


class ResearchPlan(BaseModel):
    """Research Manager's adjudication of the bull/bear debate."""
    recommendation: PortfolioRating = Field(description="One of Buy/Overweight/Hold/Underweight/Sell.")
    rationale: str = Field(description="Why this stance wins, weighing both sides of the debate.")
    strategic_actions: str = Field(description="Concrete instructions for the trader.")


def render_research_plan(p: ResearchPlan) -> str:
    return "\n".join([
        f"**Recommendation**: {p.recommendation.value}",
        "",
        f"**Rationale**: {p.rationale}",
        "",
        f"**Strategic Actions**: {p.strategic_actions}",
    ])


class TradeProposal(BaseModel):
    """Trader's concrete proposal from the investment plan."""
    action: TraderAction = Field(description="Buy, Hold, or Sell.")
    reasoning: str = Field(description="2–4 sentence justification.")
    size_pct: float | None = Field(default=None, description="Target position size as % of portfolio.")
    entry: str | None = Field(default=None, description="Entry approach, e.g. staged / immediate.")


def render_trade_proposal(p: TradeProposal) -> str:
    parts = [f"**Action**: {p.action.value}", "", f"**Reasoning**: {p.reasoning}"]
    if p.size_pct is not None:
        parts += ["", f"**Size**: {p.size_pct:.1f}%"]
    if p.entry:
        parts += ["", f"**Entry**: {p.entry}"]
    return "\n".join(parts)


class PortfolioDecision(BaseModel):
    """Portfolio Manager's final decision after the risk debate."""
    rating: PortfolioRating = Field(description="Final rating: Buy/Overweight/Hold/Underweight/Sell.")
    executive_summary: str = Field(description="2–4 sentence action plan.")
    investment_thesis: str = Field(description="Detailed reasoning, weighing the risk debate.")
    price_target: float | None = Field(default=None, description="Optional price target.")
    time_horizon: str | None = Field(default=None, description="Optional horizon, e.g. 3–6 months.")


def render_pm_decision(d: PortfolioDecision) -> str:
    parts = [
        f"**Rating**: {d.rating.value}",
        "",
        f"**Executive Summary**: {d.executive_summary}",
        "",
        f"**Investment Thesis**: {d.investment_thesis}",
    ]
    if d.price_target is not None:
        parts += ["", f"**Price Target**: {d.price_target}"]
    if d.time_horizon:
        parts += ["", f"**Time Horizon**: {d.time_horizon}"]
    return "\n".join(parts)


_RATING_RE = re.compile(r"\*\*Rating\*\*:\s*([A-Za-z]+)")


def parse_rating(final_decision: str) -> str:
    """Extract the headline rating word from a rendered PM decision."""
    m = _RATING_RE.search(final_decision or "")
    if m:
        return m.group(1).capitalize()
    # loose fallback
    for r in ("Overweight", "Underweight", "Buy", "Sell", "Hold"):
        if r.lower() in (final_decision or "").lower():
            return r
    return "Hold"
