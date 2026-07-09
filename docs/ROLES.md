# Pantheon — Agent Role Specification

Every agent in Pantheon is characterized using the six-dimension design space from
Stähle et al., *"A Design Space for Intelligent Agents in Mixed-Initiative Visual
Analytics"* (arXiv:2512.23372). This document is the design contract: it defines
each agent **before** implementation, so the code and the evaluation both speak the
same vocabulary.

**Architecture:** Pantheon mirrors the TradingAgents architecture — a 13-agent firm
with **two back-to-back debate structures** (a research debate and a risk debate),
each resolved by a manager acting as a judge. Pantheon adds **one** agent of its own:
the **Equity Scanner** (a human/software toggle for the discovery step).

## The six dimensions (reference)

| # | Dimension | Attributes (values used in this spec) |
|---|-----------|----------------------------------------|
| 1 | **Configuration & Logic** | Type {Human, Wizard, Software} · Role {Analyzer, Instructor, Interactor, Recommender, Explorer, Visualizer, Generator, Ranker, Judge, Summarizer, Labeler} · Model Type {Rule-Based, Generative AI, Human Brain, …} · Autonomy {Internal Deliberate, Internal Spontaneous, External} · Adaptation {Internal, External Observations, External Communication, None} |
| 2 | **World Model** | Provenance {Observation/Action/Interaction/Communication History, None} · Persistence {Continuous, Session-Based, Not Persistent} · Data Awareness · Agent Awareness · Task Awareness |
| 3 | **Observations** | Data Structure {Structured, Semi-Structured, Unstructured} · Sensor Modality {Text, Numeric, Visual, Code} · Context Level {One Input, Multiple Inputs, Whole Environment} · Synchronism · Trigger {Internal, Communication-Based, Infrastructure-Based} |
| 4 | **Communication** | Payload {Signal, Signal+Data, None} · Type Out/In {Notification, Instruction, Request, Feedback, Availability, None} · Internal Sharing {Operational, World Model, None} · Trigger |
| 5 | **Actions** | CRUD {Create, Update, Delete} · Type {Writing, Counting, Coding, Visualizing, Interacting} · Affected Scope {Entire Environment, Part of World Model, Outside of World Model} · Trigger · Delay {No Delay, Static, Metric-Based, Until Acknowledged} |
| 6 | **Infrastructure** | Initialized/Dynamic Modules {Configuration, Observation, Action, Communication} · Agent Interplay {Independent, Cooperative, Competitive} |

## Roster (14 agents)

| # | Agent | Type | Paper Role(s) | Interplay |
|---|-------|------|---------------|-----------|
| 0 | Equity Scanner *(Pantheon addition)* | Human ⇄ Software | Explorer, Ranker, Instructor, Interactor | Cooperative |
| 1 | Market Analyst | Software | Analyzer | Cooperative |
| 2 | Social Media Analyst | Software | Analyzer, Summarizer | Cooperative |
| 3 | News Analyst | Software | Analyzer | Cooperative |
| 4 | Fundamentals Analyst | Software | Analyzer | Cooperative |
| 5 | Bull Researcher | Software | Judge | Competitive (vs Bear) |
| 6 | Bear Researcher | Software | Judge | Competitive (vs Bull) |
| 7 | Research Manager | Software | Judge, Instructor | Cooperative (adjudicates research debate) |
| 8 | Trader | Software | Recommender | Cooperative |
| 9 | Aggressive Risk Analyst | Software | Judge | Competitive (risk debate) |
| 10 | Conservative Risk Analyst | Software | Judge | Competitive (risk debate) |
| 11 | Neutral Risk Analyst | Software | Judge | Competitive (risk debate) |
| 12 | Portfolio Manager | Software | Judge, Recommender | Cooperative (adjudicates risk debate) |

## Flow

```
Equity Scanner ──► Analyst Team (Market → Social → News → Fundamentals)
                        │
                        ▼
              Bull Researcher ⇄ Bear Researcher   (research debate)
                        │
                        ▼
                Research Manager   (judges debate → investment plan)
                        │
                        ▼
                     Trader        (plan → proposed trade)
                        │
                        ▼
   Aggressive ⇄ Conservative ⇄ Neutral Risk Analyst   (risk debate)
                        │
                        ▼
              Portfolio Manager    (judges risk debate → final decision)
```

---

## Agent 0 — Equity Scanner  *(Pantheon addition; the discovery step; mixed-initiative toggle)*

The single design lever that distinguishes Pantheon from TradingAgents: *who chooses
what to trade.* TradingAgents takes the ticker as a given; Pantheon makes the selection
step explicit and runtime-switchable between two configurations.

### Mode A — Human
- **1 Configuration:** Type **Human** · Role **Explorer + Instructor + Interactor** · Model Type Human Brain · Autonomy Internal Deliberate · Adaptation Internal
- **2 World Model:** Provenance Interaction History · Persistence Continuous (the person) · Task Awareness Self Aware
- **3 Observations:** Modality Visual + Text · Context Level Whole Environment · Trigger Internal
- **4 Communication:** Outgoing **Instruction** ("analyze NVDA") → Analyst Team · Payload Signal + Data
- **5 Actions:** Type **Interacting** · CRUD Create (sets target) · Scope Outside of World Model · Trigger Internal
- **6 Interplay:** external initiator (mixed-initiative anchor)

### Mode B — Software
- **1 Configuration:** Type **Software** · Role **Explorer + Ranker** · Model Type Rule-Based (+ optional Generative AI) · Autonomy Internal Spontaneous · Adaptation External Observations
- **2 World Model:** Provenance Observation History · Persistence Session-Based · Data Awareness Subpart of Observation
- **3 Observations:** Data Structure Structured (universe metrics) · Modality **Numeric** · Context Level Whole Environment · Trigger Infrastructure-Based (new session)
- **4 Communication:** Outgoing **Notification** (top-N candidates) → Analyst Team
- **5 Actions:** Type **Counting** · CRUD Create (ranked candidate list) · Scope Part of World Model
- **6 Interplay:** **Cooperative** (feeds the pipeline)

---

## Analyst Team  *(perceive & interpret — all Analyzers, differentiated by Sensor Modality)*

All four share: Type Software · Model Type Generative AI · Autonomy Internal Deliberate ·
Adaptation External Observations · World Model {Observation History, Session-Based, Aware
of Others' Tasks} · Observations Trigger Communication-Based, Context Level Multiple Inputs ·
Communication Outgoing **Notification** (their report) → Researcher Team, Internal Sharing
World Model Sharing · Actions Type Writing, CRUD Create, Scope Part of World Model ·
Interplay Cooperative. They differ on **Sensor Modality / Data Structure**:

### Agent 1 — Market Analyst
- **Role Analyzer** · Modality **Numeric + Code** (price series, technical indicators) · Data Structure Structured

### Agent 2 — Social Media Analyst
- **Role Analyzer + Summarizer** · Modality **Text** (social posts) · Data Structure Unstructured

### Agent 3 — News Analyst
- **Role Analyzer** · Modality **Text** (macro & company news) · Data Structure Unstructured

### Agent 4 — Fundamentals Analyst
- **Role Analyzer** · Modality **Numeric** (financial statements, ratios) · Data Structure Structured

---

## Research Team  *(structured debate + adjudication)*

### Agent 5 — Bull Researcher
- **1 Configuration:** Type Software · Role **Judge** · Model Type Generative AI · Autonomy Internal Deliberate · Adaptation External Communication
- **2 World Model:** Agent Awareness Aware of all Agents · Provenance Communication History · Task Awareness Aware of Others' Tasks
- **3 Observations:** Modality Text · Context Level Whole Environment (analyst reports + debate so far) · Trigger Communication-Based
- **4 Communication:** Incoming **Feedback** (from Bear) · Outgoing **Feedback** (bull case) · Internal Sharing World Model Sharing
- **5 Actions:** Type Writing · CRUD Create/Update (argument) · Scope Part of World Model
- **6 Interplay:** **Competitive** with Bear Researcher

### Agent 6 — Bear Researcher
- *Symmetric to Bull.* Type Software · Role **Judge** · Outgoing **Feedback** (bear case) · **Interplay: Competitive** with Bull.

### Agent 7 — Research Manager  *(debate facilitator / judge)*
- **1 Configuration:** Type Software · Role **Judge + Instructor** · Model Type Generative AI · Autonomy Internal Deliberate · Adaptation External Communication
- **2 World Model:** Agent Awareness Aware of all Agents · Provenance Communication History · Data Awareness Full
- **3 Observations:** Modality Text · Context Level Whole Environment (full bull/bear history) · Trigger Communication-Based
- **4 Communication:** Incoming Feedback (both researchers) · Outgoing **Instruction** (the investment plan) → Trader
- **5 Actions:** Type Writing · CRUD Create (investment plan; commits to a stance) · Scope Part of World Model
- **6 Interplay:** Cooperative (resolves the Competitive research debate)

---

## Execution & Risk

### Agent 8 — Trader
- **1 Configuration:** Type Software · Role **Recommender** · Model Type Generative AI · Autonomy Internal Deliberate · Adaptation External Communication
- **2 World Model:** Task Awareness Aware of Others' Tasks · Data Awareness Full
- **3 Observations:** Context Level Whole Environment (investment plan + reports) · Trigger Communication-Based
- **4 Communication:** Incoming Instruction (plan from Research Manager) · Outgoing **Request** (proposed trade) → Risk debate
- **5 Actions:** Type Writing · CRUD **Create** (proposed trade: side, size, timing) · Scope Part of World Model
- **6 Interplay:** Cooperative

### Agents 9–11 — Risk Debate  *(three competing stances on the trade)*
Shared: Type Software · Role **Judge** · Model Type Generative AI · Autonomy Internal
Deliberate · Adaptation External Communication · Observations {Text, Whole Environment,
Communication-Based} · Communication Incoming Request (Trader's decision) + Feedback (other
debators), Outgoing **Feedback** (their stance) · Actions Writing, Create/Update argument ·
**Interplay: Competitive** (three-way).

- **Agent 9 — Aggressive Risk Analyst** — champions high-reward / high-risk upside.
- **Agent 10 — Conservative Risk Analyst** — champions caution / capital preservation.
- **Agent 11 — Neutral Risk Analyst** — balances the two extremes.

### Agent 12 — Portfolio Manager  *(risk-debate judge / final decision)*
- **1 Configuration:** Type Software · Role **Judge + Recommender** · Model Type Generative AI · Autonomy Internal Deliberate · Adaptation External Communication
- **2 World Model:** Agent Awareness Aware of all Agents · Persistence **Continuous** (portfolio state across runs) · Data Awareness Full · Provenance Communication + Action History
- **3 Observations:** Modality Text · Context Level Whole Environment (full risk-debate history) · Trigger Communication-Based
- **4 Communication:** Incoming Feedback (three risk analysts) · Outgoing **Instruction** (execute final decision)
- **5 Actions:** CRUD **Update** (portfolio: holdings, cash) · Scope Part of World Model ·
  **Delay: Delayed until Action Acknowledged** *(only if human-approval mode is enabled)*
- **6 Interplay:** Cooperative (resolves the Competitive risk debate)

---

## System-level (Dimension 6 — Infrastructure)

- **Initialized Modules:** Configuration · Observation · Action · Communication
- **Dynamic Modules:** Action Module (spawned per analysis / per trade) ·
  **Trigger:** Based on Agents (the Trader's proposal spawns the risk debate) and Based on Environment (new data)
- **Agent Interplay across the system:**
  - **Cooperative** pipeline: Scanner → Analysts → Research Manager → Trader → Portfolio Manager
  - **Competitive** channels: Bull vs Bear (research debate); Aggressive vs Conservative vs Neutral (risk debate)
  - Two **judge** agents resolve the two debates: Research Manager, Portfolio Manager

## Role coverage (against the paper's 11 roles)

Covered: Analyzer, Summarizer, Explorer, Ranker, Instructor, Interactor, Judge, Recommender.
Not used: Visualizer (would need a charting agent), Generator, Labeler.
