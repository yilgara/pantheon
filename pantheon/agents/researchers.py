"""Research debate — Bull vs Bear (Judges, competitive).

Each reads all analyst reports plus the running debate transcript, argues its
side (rebutting the opponent's last point), appends its turn, and increments
the shared count that drives termination.
"""

from __future__ import annotations


def _reports(state) -> str:
    return (
        f"Market report:\n{state['market_report']}\n\n"
        f"Sentiment report:\n{state['sentiment_report']}\n\n"
        f"News report:\n{state['news_report']}\n\n"
        f"Fundamentals report:\n{state['fundamentals_report']}"
    )


def _make_researcher(side: str, llm):
    other = "bear" if side == "bull" else "bull"
    stance = (
        "Argue the BULLISH case: why this is a compelling long."
        if side == "bull" else
        "Argue the BEARISH case: the risks, downside, and reasons to avoid or short."
    )

    def node(state) -> dict:
        debate = state["research_debate"]
        prompt = (
            f"You are the {side.capitalize()} Researcher debating {state['ticker']}.\n"
            f"{stance} Be specific and use the reports. Directly rebut the last "
            f"{other} argument if there is one. Keep it to 4-6 sentences.\n\n"
            f"{_reports(state)}\n\n"
            f"Debate so far:\n{debate['history'] or '(you speak first)'}\n\n"
            f"Last {other} argument:\n{debate['current_response'] or '(none yet)'}"
        )
        content = llm.invoke(prompt).content
        turn = f"{side.capitalize()} Researcher: {content}"

        updated = dict(debate)
        updated["history"] = (debate["history"] + "\n" + turn).strip()
        updated[f"{side}_history"] = (debate[f"{side}_history"] + "\n" + turn).strip()
        updated["current_response"] = turn
        updated["count"] = debate["count"] + 1
        return {"research_debate": updated, "sender": f"{side.capitalize()} Researcher"}

    return node


def create_bull_researcher(llm):
    return _make_researcher("bull", llm)


def create_bear_researcher(llm):
    return _make_researcher("bear", llm)
