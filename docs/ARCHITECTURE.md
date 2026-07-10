# Pantheon — Build Architecture

Clean-room build plan derived from studying the TradingAgents reference (approaches
only — no code copied). This is the contract for how we implement the two layers.

---

## Layer 1 — Data

**Pattern to replicate (simplified):**

```
agent tools (@tool)  ─►  router.get(category, ...)  ─►  provider fn  ─►  formatted string
                                                              │
                                                         disk cache (CSV)
```

- **One router** (`pantheon/data/router.py`) maps a *category* → a provider function, with an ordered fallback list. Categories: `stock`, `indicators`, `fundamentals`, `news`, `macro`.
- **Providers return strings** (CSV / markdown), not JSON — the LLM reads prose. Keeps the tool layer trivial.
- **`@tool`-decorated wrappers** (`pantheon/agents/tools.py`) wrap router calls; the docstring is the tool description the LLM sees.
- **Per-symbol disk cache** keyed by `{symbol}-{start}-{end}.csv`, with a staleness guard.
- **Error taxonomy**: `NoData` / `RateLimit` / `NotConfigured` → router tries the next provider; optional categories degrade to a sentinel string instead of crashing.

**Pantheon simplifications:**
- Start with **yfinance only** (free, no key) for `stock` + `indicators` + `fundamentals` + `news`; add FRED (`macro`) later. Skip Alpha Vantage / Reddit / StockTwits / Polymarket for v1.
- No crypto/forex symbol normalization initially (stocks only).
- A `mock` provider so the whole pipeline runs offline / for tests.

---

## Layer 2 — Workflow (LangGraph)

### State (`pantheon/graph/state.py`)
A `TypedDict` extending `MessagesState`, mirroring the reference:
- Scalars: `ticker`, `trade_date`, `sender`
- Analyst reports (strings): `market_report`, `sentiment_report`, `news_report`, `fundamentals_report`
- `research_debate`: `{bull_history, bear_history, history, current_response, judge_decision, count}`
- `investment_plan` (Research Manager output), `trade_proposal` (Trader output)
- `risk_debate`: `{aggressive_history, conservative_history, neutral_history, history, latest_speaker, count, judge_decision}`
- `final_decision`
- **Pantheon addition:** `selected_by` (fixed `"human"` — the Equity Scanner is a human who supplies the ticker)

**Key idea:** debate transcripts are plain **concatenated strings**; `count` drives termination (no content parsing).

### Agent pattern (`pantheon/agents/*.py`)
Every agent is a **factory returning a node closure**:
```python
def create_market_analyst(llm):
    def node(state) -> dict:      # returns state deltas only
        ...
        return {"messages": [result], "market_report": report}
    return node
```
- **Analysts** bind tools and loop until no `tool_calls`, then write their report.
- **Debaters** read `history` + last opponent response, append their turn, increment `count`.
- **Managers/Trader** use **structured output** (`with_structured_output(schema)`) with a **plain-text fallback** if the provider/model can't do it; a `render_*` fn turns the Pydantic object into markdown for the state.

### Structured output (`pantheon/agents/schemas.py`)
Pydantic models + renderers: `ResearchPlan`, `TradeProposal`, `PortfolioDecision`.
Helper `invoke_structured_or_freetext(structured_llm, plain_llm, prompt, render)`.

### Graph wiring (`pantheon/graph/build.py`)
`StateGraph(State)` with:
1. **Human ticker selection** — the human (Equity Scanner) supplies the ticker into `create_initial_state`; the graph starts at the first analyst (no scanner node)
2. Analysts chained sequentially, each with a **tool-loop** (conditional edge on `tool_calls` → tool node → back; else → next analyst)
3. Last analyst → **Bull**; Bull⇄Bear conditional loop (`count >= 2*max_debate_rounds` → Research Manager)
4. Research Manager → Trader → Aggressive
5. Risk cycle Aggressive→Conservative→Neutral (`count >= 3*max_risk_rounds` → Portfolio Manager)
6. Portfolio Manager → END

### Run lifecycle (`pantheon/graph/run.py`)
- `create_initial_state(ticker, trade_date, selected_by, ...)` with all debate counts at 0.
- Invoke via `.stream(stream_mode="values")` (so the UI/tracer can watch node deltas) or `.invoke()`.
- Extract `final_decision` with a small regex parser (no LLM).

**Pantheon simplifications / deferrals:**
- **Defer** memory/reflection (the two-phase outcome learning) and the SQLite checkpointer to a later pass.
- **Add** a tracing callback that records every node delta as a structured event (feeds the eval layer + the UI stream).

---

## What's ours vs. replicated

| Piece | Source |
|---|---|
| Human Equity Scanner (human supplies the ticker) | **Pantheon (new)** |
| Structured event tracing | **Pantheon (new)** |
| State shape, agent factory pattern, debate loops, graph wiring | Clean-room reimpl of the reference approach |
| Data router + string providers + @tool wrappers + disk cache | Clean-room reimpl of the reference approach |

## Build order
1. **Config + LLM client** (`pantheon/config.py`, `pantheon/llm.py`)
2. **Data layer** (router + yfinance provider + mock + `@tool` wrappers)
3. **State + schemas**
4. **Agents** (analysts → researchers → managers → trader → risk)
5. **Graph wiring + run**
6. **Scanner node** + **tracing callback**
7. Wire the **backend** (FastAPI) → replace the frontend mock with the live stream
