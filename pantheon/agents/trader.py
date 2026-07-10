"""Trader — turns the Research Manager's plan into a concrete trade proposal."""

from __future__ import annotations

from pantheon.agents.schemas import TradeProposal, render_trade_proposal
from pantheon.agents.structured import bind_structured, invoke_structured_or_freetext


def create_trader(llm):
    structured = bind_structured(llm, TradeProposal, "Trader")

    def node(state) -> dict:
        prompt = (
            f"You are the Trader for {state['ticker']}. Turn the investment plan into a concrete, "
            "actionable proposal: an action (Buy/Hold/Sell), a target position size (% of portfolio), "
            "and an entry approach (e.g. immediate vs staged). Keep the reasoning to 2-4 sentences.\n\n"
            f"Investment plan:\n{state['investment_plan']}"
        )
        proposal = invoke_structured_or_freetext(structured, llm, prompt, render_trade_proposal, "Trader")
        return {"trade_proposal": proposal, "sender": "Trader"}

    return node
