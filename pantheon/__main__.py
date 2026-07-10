"""CLI: python -m pantheon TICKER DATE [--provider ...] [--mock]

Loads .env (for API keys), runs a full analysis, and prints the reports and
final decision.
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv


def main(argv: list[str] | None = None) -> int:
    load_dotenv()  # pick up OPENAI_API_KEY / ANTHROPIC_API_KEY / etc. from .env

    p = argparse.ArgumentParser(prog="pantheon")
    p.add_argument("ticker", help="e.g. NVDA")
    p.add_argument("date", help="trade date, yyyy-mm-dd")
    p.add_argument("--provider", help="openai | anthropic | google | ollama")
    p.add_argument("--deep", help="deep-think model id")
    p.add_argument("--quick", help="quick-think model id")
    p.add_argument("--mock", action="store_true", help="force offline mock data")
    args = p.parse_args(argv)

    from pantheon.config import get_config, set_config

    overrides: dict = {}
    if args.provider:
        overrides["llm_provider"] = args.provider
    if args.deep:
        overrides["deep_think_llm"] = args.deep
    if args.quick:
        overrides["quick_think_llm"] = args.quick
    if args.mock:
        cats = ["stock", "indicators", "fundamentals", "news", "social", "macro", "prediction_markets"]
        overrides["data_vendors"] = {c: "mock" for c in cats}
    if overrides:
        set_config(overrides)

    cfg = get_config()
    print(f"▶ Analyzing {args.ticker} @ {args.date} "
          f"[{cfg['llm_provider']}: {cfg['quick_think_llm']} / {cfg['deep_think_llm']}]"
          f"{' · MOCK data' if args.mock else ''}\n")

    from pantheon.graph.run import run_pipeline
    final, signal = run_pipeline(args.ticker, args.date, config=cfg)

    for label, key in [("Market", "market_report"), ("Social", "sentiment_report"),
                       ("News", "news_report"), ("Fundamentals", "fundamentals_report")]:
        print(f"── {label} Analyst ──\n{final[key]}\n")
    print(f"── Investment Plan (Research Manager) ──\n{final['investment_plan']}\n")
    print(f"── Trade Proposal ──\n{final['trade_proposal']}\n")
    print(f"── FINAL DECISION (Portfolio Manager) ──\n{final['final_decision']}\n")
    print(f"★ SIGNAL: {signal}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
