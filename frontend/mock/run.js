// Mock run data for Pantheon UI development.
// Shape mirrors what the real backend trace will provide: an ordered list of
// steps, each tagged with the agent, its team, and its output. Swapped for a
// live API call later. Exposed as a global so it works over file:// (no fetch).

window.PANTHEON_MOCK = {
  ticker: "NVDA",
  trade_date: "2024-05-10",
  universe: ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD"],

  // Scanner step differs by mode; everything after is shared.
  scanner: {
    human: {
      agent: "Equity Scanner", team: "scanner", role: "Explorer + Instructor (Human)",
      content: "Human analyst selected **NVDA** as the target to analyze.",
    },
    agent: {
      agent: "Equity Scanner", team: "scanner", role: "Explorer + Ranker (Software)",
      content: "Screened 8 tickers by 60-day momentum and selected the top candidate: **NVDA**.",
      ranking: [
        { ticker: "NVDA", score: 0.284 },
        { ticker: "META", score: 0.191 },
        { ticker: "AMD", score: 0.147 },
        { ticker: "GOOGL", score: 0.093 },
        { ticker: "MSFT", score: 0.071 },
        { ticker: "AMZN", score: 0.052 },
        { ticker: "AAPL", score: -0.014 },
        { ticker: "TSLA", score: -0.088 },
      ],
    },
  },

  // Shared pipeline (analysts -> research debate -> manager -> trader -> risk debate -> PM)
  steps: [
    { agent: "Market Analyst", team: "analyst", role: "Analyzer · Numeric+Code",
      content: "Price up 28% over 60 days; RSI 71 (overbought), but MACD still positive and above signal line. Trend intact, momentum strong but extended." },
    { agent: "Social Media Analyst", team: "analyst", role: "Analyzer + Summarizer · Text",
      content: "Retail sentiment overwhelmingly bullish (fear-of-missing-out tone). Mentions up 3x week-over-week. Crowd euphoria is itself a mild caution flag." },
    { agent: "News Analyst", team: "analyst", role: "Analyzer · Text",
      content: "Datacenter demand headlines strong; upcoming earnings a catalyst. No adverse regulatory news. Macro backdrop neutral-to-supportive." },
    { agent: "Fundamentals Analyst", team: "analyst", role: "Analyzer · Numeric",
      content: "Revenue +262% YoY, gross margin ~78%. Valuation rich (fwd P/E ~35) but justified if datacenter growth persists. Balance sheet solid." },

    { agent: "Bull Researcher", team: "bull", role: "Judge · debate R1",
      content: "The fundamentals are extraordinary — triple-digit revenue growth with expanding margins. Momentum + catalyst (earnings) = asymmetric upside. Overbought is a feature of leaders." },
    { agent: "Bear Researcher", team: "bear", role: "Judge · debate R1",
      content: "Growth that steep mean-reverts. RSI 71 into earnings is a setup for a 'sell-the-news' drop. Valuation leaves no margin for a single soft guide. Crowd euphoria = late-stage." },

    { agent: "Research Manager", team: "manager", role: "Judge + Instructor",
      content: "The bull case is stronger on evidence: growth and catalyst outweigh the overbought signal. **Investment plan: establish a moderate long, sized to survive earnings volatility.** Do not go all-in given the extended RSI." },

    { agent: "Trader", team: "trader", role: "Recommender",
      content: "**Proposed trade: BUY NVDA, 6% of portfolio, staged entry (half now, half post-earnings).** Timing: initiate before the catalyst; scale on confirmation." },

    { agent: "Aggressive Risk Analyst", team: "risk-aggressive", role: "Judge · risk R1",
      content: "6% is timid for a setup this good. Push to 9–10% — the datacenter cycle is early and this is the purest exposure. Missing the move is the real risk." },
    { agent: "Conservative Risk Analyst", team: "risk-conservative", role: "Judge · risk R1",
      content: "Into earnings with RSI 71? A 6% position can gap down 10%+ overnight. Cut to 3% or wait for the print. Capital preservation first." },
    { agent: "Neutral Risk Analyst", team: "risk-neutral", role: "Judge · risk R1",
      content: "The staged entry already balances this. Keep the 6% target but respect the half-now/half-later structure — it hedges the earnings gap without giving up the trend." },

    { agent: "Portfolio Manager", team: "pm", role: "Judge + Recommender",
      content: "Weighing the risk debate, the neutral stance is most consistent with the plan. **Final decision: BUY NVDA, 6% target, staged (3% now, 3% after earnings confirmation).**",
      decision: { action: "BUY", ticker: "NVDA", size_pct: 6, entry: "staged (3% now / 3% post-earnings)" } },
  ],

  portfolio_before: { cash: 100000, positions: [], risk_score: 0.0 },
  portfolio_after: {
    cash: 97000,
    positions: [{ ticker: "NVDA", weight_pct: 3.0, note: "half of 6% target; remainder staged" }],
    risk_score: 4.8,
  },
};
