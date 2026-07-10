"""Manager agents — the two judges.

Research Manager adjudicates the bull/bear debate into an investment plan.
Portfolio Manager adjudicates the risk debate into the final decision. Both
use structured output (with a plain-text fallback).
"""

from __future__ import annotations

from pantheon.agents.schemas import (
    PortfolioDecision,
    ResearchPlan,
    render_pm_decision,
    render_research_plan,
)
from pantheon.agents.structured import bind_structured, invoke_structured_or_freetext


def create_research_manager(llm):
    structured = bind_structured(llm, ResearchPlan, "Research Manager")

    def node(state) -> dict:
        debate = state["research_debate"]
        prompt = (
            f"You are the Research Manager and debate facilitator for {state['ticker']}.\n"
            "Critically weigh the bull and bear arguments and commit to a clear stance "
            "(Buy / Overweight / Hold / Underweight / Sell). Reserve Hold only for genuinely "
            "balanced evidence. Produce a rationale and concrete strategic actions for the trader.\n\n"
            f"Full debate:\n{debate['history']}"
        )
        plan = invoke_structured_or_freetext(structured, llm, prompt, render_research_plan, "Research Manager")
        updated = dict(debate)
        updated["judge_decision"] = plan
        return {"research_debate": updated, "investment_plan": plan, "sender": "Research Manager"}

    return node


def create_portfolio_manager(llm):
    structured = bind_structured(llm, PortfolioDecision, "Portfolio Manager")

    def node(state) -> dict:
        risk = state["risk_debate"]
        prompt = (
            f"You are the Portfolio Manager making the final call on {state['ticker']}.\n"
            "Weigh the aggressive, conservative, and neutral risk analysts against the trader's "
            "proposal and the investment plan. Deliver a final rating (Buy / Overweight / Hold / "
            "Underweight / Sell), an executive summary, and an investment thesis. Optionally a "
            "price target and time horizon.\n\n"
            f"Investment plan:\n{state['investment_plan']}\n\n"
            f"Trader proposal:\n{state['trade_proposal']}\n\n"
            f"Risk debate:\n{risk['history']}"
        )
        decision = invoke_structured_or_freetext(structured, llm, prompt, render_pm_decision, "Portfolio Manager")
        updated = dict(risk)
        updated["judge_decision"] = decision
        return {"risk_debate": updated, "final_decision": decision, "sender": "Portfolio Manager"}

    return node
