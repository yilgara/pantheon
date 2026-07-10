// Pantheon dashboard — drives a live run over Server-Sent Events.

const PIPELINE = [
  ["Analysts", [["Market Analyst", "analyst"], ["Social Media Analyst", "analyst"],
                ["News Analyst", "analyst"], ["Fundamentals Analyst", "analyst"]]],
  ["Research debate", [["Bull Researcher", "bull"], ["Bear Researcher", "bear"]]],
  ["Adjudication", [["Research Manager", "manager"]]],
  ["Execution", [["Trader", "trader"]]],
  ["Risk debate", [["Aggressive Analyst", "risk-aggressive"],
                   ["Conservative Analyst", "risk-conservative"],
                   ["Neutral Analyst", "risk-neutral"]]],
  ["Decision", [["Portfolio Manager", "pm"]]],
];
const COMPETITIVE = new Set(["bull", "bear", "risk-aggressive", "risk-conservative", "risk-neutral"]);
const BULLISH = new Set(["Buy", "Overweight"]);
const BEARISH = new Set(["Sell", "Underweight"]);

const $ = (s) => document.querySelector(s);
const md = (s) => (s || "").replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>");
let source = null;

function renderPipeline() {
  const el = $("#pipeline"); el.innerHTML = "";
  for (const [label, nodes] of PIPELINE) {
    const l = document.createElement("div");
    l.className = "stage-label"; l.textContent = label; el.appendChild(l);
    for (const [name, team] of nodes) {
      const n = document.createElement("div");
      n.className = "node"; n.dataset.agent = name;
      n.innerHTML = `<span class="swatch" style="background:var(--${team})"></span><span>${name}</span><span class="tick">✓</span>`;
      el.appendChild(n);
    }
  }
}
function setNode(name, state) {
  const n = document.querySelector(`.node[data-agent="${CSS.escape(name)}"]`);
  if (!n) return;
  document.querySelectorAll(".node.active").forEach((x) => x.classList.remove("active"));
  if (state === "active") n.classList.add("active");
  if (state === "done") { n.classList.remove("active"); n.classList.add("done"); }
}

function addMessage(ev) {
  const div = document.createElement("div");
  div.className = `msg t-${ev.team}`;
  const comp = COMPETITIVE.has(ev.team) ? `<span class="debate-tag tag-competitive">competitive</span>` : "";
  div.innerHTML =
    `<div class="head"><span class="agent">${ev.agent}</span>` +
    `<span class="role">${ev.role || ""}</span>${comp}</div>` +
    `<div class="body">${md(ev.content)}</div>`;
  $("#feed").appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
}

function showDecision(rating, ticker) {
  $("#decision").classList.remove("hidden");
  const a = $("#decision-action");
  const cls = BULLISH.has(rating) ? "BUY" : BEARISH.has(rating) ? "SELL" : "HOLD";
  a.textContent = `${rating} ${ticker}`;
  a.className = `decision-action ${cls}`;
  $("#decision-meta").textContent = "Full reasoning in the Portfolio Manager message.";
}

function setStatus(text, busy) {
  $("#status").textContent = text;
  $("#run").disabled = !!busy;
}

function run() {
  if (source) source.close();
  const ticker = ($("#ticker").value || "NVDA").trim().toUpperCase();
  const date = ($("#date").value || "2024-05-10").trim();
  $("#feed").innerHTML = "";
  $("#decision").classList.add("hidden");
  renderPipeline();
  setStatus("running…", true);
  $("#runinfo-body").innerHTML = `Ticker <b>${ticker}</b> · as of ${date}`;

  const t0 = Date.now();
  source = new EventSource(`/api/stream?ticker=${encodeURIComponent(ticker)}&date=${encodeURIComponent(date)}`);

  source.onmessage = (e) => {
    const ev = JSON.parse(e.data);
    if (ev.error) {
      addMessage({ agent: "Error", team: "bear", role: "", content: ev.error });
      setStatus("error", false); source.close(); return;
    }
    if (ev.done) {
      const secs = ((Date.now() - t0) / 1000).toFixed(0);
      setStatus(`done · ${ev.signal} · ${secs}s`, false);
      $("#runinfo-body").innerHTML += `<br>Signal <b>${ev.signal}</b> · ${secs}s`;
      source.close(); return;
    }
    setNode(ev.agent, "active");
    addMessage(ev);
    setNode(ev.agent, "done");
    if (ev.decision) showDecision(ev.decision, ticker);
  };
  source.onerror = () => { setStatus("connection closed", false); if (source) source.close(); };
}

$("#run").addEventListener("click", run);
renderPipeline();
