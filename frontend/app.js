// Pantheon UI — replays a mock run with a light streaming effect.
// Swap `buildSequence()` / the mock for a live backend stream later.

const MOCK = window.PANTHEON_MOCK;
let mode = "human";
let running = false;

// Pipeline definition: stage label -> nodes (agent name + team for color).
const PIPELINE = [
  ["Discovery", [["Equity Scanner", "scanner"]]],
  ["Analysts", [["Market Analyst", "analyst"], ["Social Media Analyst", "analyst"],
                ["News Analyst", "analyst"], ["Fundamentals Analyst", "analyst"]]],
  ["Research debate", [["Bull Researcher", "bull"], ["Bear Researcher", "bear"]]],
  ["Adjudication", [["Research Manager", "manager"]]],
  ["Execution", [["Trader", "trader"]]],
  ["Risk debate", [["Aggressive Risk Analyst", "risk-aggressive"],
                   ["Conservative Risk Analyst", "risk-conservative"],
                   ["Neutral Risk Analyst", "risk-neutral"]]],
  ["Decision", [["Portfolio Manager", "pm"]]],
];

const COMPETITIVE = new Set(["bull", "bear", "risk-aggressive", "risk-conservative", "risk-neutral"]);
const $ = (s) => document.querySelector(s);
const money = (n) => "$" + n.toLocaleString("en-US");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const md = (s) => s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

// ---------- Pipeline rendering ----------
function renderPipeline() {
  const el = $("#pipeline");
  el.innerHTML = "";
  for (const [label, nodes] of PIPELINE) {
    const l = document.createElement("div");
    l.className = "stage-label";
    l.textContent = label;
    el.appendChild(l);
    for (const [name, team] of nodes) {
      const n = document.createElement("div");
      n.className = "node";
      n.dataset.agent = name;
      n.innerHTML = `<span class="swatch" style="background:var(--${team})"></span>` +
                    `<span>${name}</span><span class="tick">✓</span>`;
      el.appendChild(n);
    }
  }
}
function setNode(name, state) {
  const n = document.querySelector(`.node[data-agent="${CSS.escape(name)}"]`);
  if (!n) return;
  n.classList.remove("active", "done");
  if (state) n.classList.add(state);
}

// ---------- Feed rendering ----------
function addMessage(step) {
  const div = document.createElement("div");
  div.className = `msg t-${step.team}`;
  const competitive = COMPETITIVE.has(step.team)
    ? `<span class="debate-tag tag-competitive">competitive</span>` : "";
  let extra = "";
  if (step.ranking) {
    extra = `<div class="ranking">` + step.ranking.map((r, i) =>
      `<div class="${i === 0 ? "top" : ""}"><span>${r.ticker}</span><span>${(r.score * 100).toFixed(1)}%</span></div>`
    ).join("") + `</div>`;
  }
  div.innerHTML =
    `<div class="head"><span class="agent">${step.agent}</span>` +
    `<span class="role">${step.role}</span>${competitive}</div>` +
    `<div class="body">${md(step.content)}${extra}</div>`;
  $("#feed").appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
}

// ---------- Decision + portfolio ----------
function showDecision(d) {
  $("#decision").classList.remove("hidden");
  const a = $("#decision-action");
  a.textContent = `${d.action} ${d.ticker}`;
  a.className = `decision-action ${d.action}`;
  $("#decision-meta").innerHTML = `Size: <b>${d.size_pct}%</b> &middot; Entry: ${d.entry}`;
}
function updatePortfolio(pf) {
  $("#pf-cash").textContent = money(pf.cash);
  $("#pf-risk").textContent = pf.risk_score.toFixed(1);
  $("#pf-positions").innerHTML = pf.positions.length
    ? pf.positions.map((p) => `<b>${p.ticker}</b> — ${p.weight_pct}% <span style="opacity:.7">(${p.note})</span>`).join("<br>")
    : "No positions.";
}

// ---------- Run ----------
function buildSequence() {
  const scanner = MOCK.scanner[mode];
  return [scanner, ...MOCK.steps];
}

async function run() {
  if (running) return;
  running = true;
  $("#run").disabled = true;
  $("#feed").innerHTML = "";
  $("#decision").classList.add("hidden");
  updatePortfolio(MOCK.portfolio_before);
  renderPipeline();

  for (const step of buildSequence()) {
    setNode(step.agent, "active");
    await sleep(650);
    addMessage(step);
    setNode(step.agent, "done");
    if (step.decision) showDecision(step.decision);
    await sleep(250);
  }
  updatePortfolio(MOCK.portfolio_after);
  running = false;
  $("#run").disabled = false;
}

// ---------- Wiring ----------
$("#mode-toggle").addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  mode = btn.dataset.mode;
  document.querySelectorAll("#mode-toggle button").forEach((b) => b.classList.toggle("active", b === btn));
  $("#input-human").style.display = mode === "human" ? "" : "none";
  $("#input-agent").style.display = mode === "agent" ? "" : "none";
});
$("#run").addEventListener("click", run);

renderPipeline();
