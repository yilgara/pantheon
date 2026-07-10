"""Risk debate — three competing stances on the trade (Judges, competitive).

Aggressive / Conservative / Neutral each critique the trader's proposal from
their stance, rebutting the others, and cycle round-robin until the round limit.
"""

from __future__ import annotations

_STANCES = {
    "Aggressive": "champion high-reward, high-risk upside; push for bolder sizing where the opportunity justifies it",
    "Conservative": "prioritize capital preservation; flag downside, tail risk, and overexposure",
    "Neutral": "balance the aggressive and conservative views; find the risk-adjusted middle ground",
}


def _make_risk_debator(stance: str, llm):
    key = stance.lower()
    directive = _STANCES[stance]

    def node(state) -> dict:
        risk = state["risk_debate"]
        others = [s for s in _STANCES if s != stance]
        prompt = (
            f"You are the {stance} Risk Analyst evaluating the proposed trade on {state['ticker']}. "
            f"Your role: {directive}. Respond directly to the other analysts where relevant. "
            "Keep it to 3-5 sentences.\n\n"
            f"Trader's proposal:\n{state['trade_proposal']}\n\n"
            f"Risk debate so far:\n{risk['history'] or '(you speak first)'}\n\n"
            + "".join(
                f"Last {o} argument:\n{risk[f'current_{o.lower()}_response'] or '(none)'}\n\n"
                for o in others
            )
        )
        content = llm.invoke(prompt).content
        turn = f"{stance} Analyst: {content}"

        updated = dict(risk)
        updated["history"] = (risk["history"] + "\n" + turn).strip()
        updated[f"{key}_history"] = (risk[f"{key}_history"] + "\n" + turn).strip()
        updated[f"current_{key}_response"] = turn
        updated["latest_speaker"] = stance
        updated["count"] = risk["count"] + 1
        return {"risk_debate": updated, "sender": f"{stance} Risk Analyst"}

    return node


def create_aggressive_debator(llm):
    return _make_risk_debator("Aggressive", llm)


def create_conservative_debator(llm):
    return _make_risk_debator("Conservative", llm)


def create_neutral_debator(llm):
    return _make_risk_debator("Neutral", llm)
