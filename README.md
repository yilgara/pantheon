# Pantheon

A multi-agent **investment fund** system.

Pantheon's agents are designed around the role taxonomy and six-dimension design space
from Stähle et al., *"A Design Space for Intelligent Agents in Mixed-Initiative Visual
Analytics"* (arXiv:2512.23372). The concepts (agent roles, initiative-sharing, the
observe/act/communicate dimensions) inform the design; **all code here is original.**

## Status

Building from a clean slate, one module at a time. Nothing implemented yet.

## Planned shape

```
pantheon/
├── agents/        # the fund's agents (Analyzer / Judge / Recommender / Scanner ...)
├── orchestration/ # wiring the agents into a run
├── tracing.py     # structured event log (traces for the evaluation library)
├── scanner.py     # Equity Scanner: human/agent toggle (the discovery step)
└── eval/          # adapter to the researcher's evaluation library
backend/           # HTTP API over the fund
frontend/          # web UI (mode toggle, live agent feed, decision view)
```

## References

- Stähle et al., *A Design Space for Intelligent Agents in Mixed-Initiative Visual
  Analytics*, arXiv:2512.23372.
