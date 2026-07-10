# Pantheon — Agent Role Specification

Every agent in Pantheon is characterized using the six-dimension design space from
Stähle et al., *"A Design Space for Intelligent Agents in Mixed-Initiative Visual
Analytics"* (arXiv:2512.23372). This document is the design contract: it defines
each agent **before** implementation, so the code and the evaluation both speak the
same vocabulary.

**Architecture:** 14-agent firm with **two back-to-back debate structures** (a research debate and a risk debate),
each resolved by a manager acting as a judge. **One** human agent: the **Equity Scanner**.
> New to the vocabulary? See [`DIMENSIONS.md`](DIMENSIONS.md) for a plain-English
> explanation of every dimension and value 


## Roster (14 agents)

| # | Agent | Type | Paper Role(s) | Interplay |
|---|-------|------|---------------|-----------|
| 0 | Equity Scanner | Human | Explorer, Instructor, Interactor | Cooperative |
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

## Agent 0 — Equity Scanner  


### Human

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: **Human** · Role: **Explorer + Instructor + Interactor**<br>Model: Human Brain · Autonomy: Internal Deliberate · Adaptation: Internal |
| **2 · World Model** | Provenance: Interaction History · Persistence: Continuous (the person) · Task Awareness: Self Aware |
| **3 · Observations** | Modality: Visual + Text · Context: Whole Environment · Trigger: Internal |
| **4 · Communication** | Outgoing: **Instruction** ("analyze NVDA") → Analyst Team · Payload: Signal + Data |
| **5 · Actions** | Type: **Interacting** · CRUD: Create (sets target) · Scope: Outside World Model · Trigger: Internal |
| **6 · Interplay** | External initiator (the mixed-initiative anchor) |



## Analyst Team  *(perceive & interpret — all Analyzers, differentiated by Sensor Modality)*

**Shared by all four analysts:**

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Observations |
| **2 · World Model** | Provenance: Observation History · Persistence: Session-Based · Task Awareness: Aware of Others' Tasks |
| **3 · Observations** | Context: Multiple Inputs · Trigger: Communication-Based |
| **4 · Communication** | Outgoing: **Notification** (their report) → Researcher Team · Internal Sharing: World Model |
| **5 · Actions** | Type: Writing · CRUD: Create · Scope: Part of World Model |
| **6 · Interplay** | Cooperative |

**They differ only on Role / Sensor Modality / Data Structure:**

| # | Agent | Role | Modality | Data Structure | Reads |
|---|-------|------|----------|----------------|-------|
| 1 | Market Analyst | Analyzer | **Numeric + Code** | Structured | price series, technical indicators |
| 2 | Social Media Analyst | Analyzer + Summarizer | **Text** | Unstructured | social posts |
| 3 | News Analyst | Analyzer | **Text** | Unstructured | macro & company news |
| 4 | Fundamentals Analyst | Analyzer | **Numeric** | Structured | financial statements, ratios |

---

## Research Team  *(structured debate + adjudication)*

### Agent 5 — Bull Researcher

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Role: **Judge** · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Communication |
| **2 · World Model** | Agent Awareness: All Agents · Provenance: Communication History · Task Awareness: Aware of Others' Tasks |
| **3 · Observations** | Modality: Text · Context: Whole Environment (analyst reports + debate so far) · Trigger: Communication-Based |
| **4 · Communication** | Incoming: **Feedback** (from Bear) · Outgoing: **Feedback** (bull case) · Internal Sharing: World Model |
| **5 · Actions** | Type: Writing · CRUD: Create/Update (argument) · Scope: Part of World Model |
| **6 · Interplay** | **Competitive** with Bear Researcher |

### Agent 6 — Bear Researcher

Symmetric to the Bull: Type Software · Role **Judge** · Outgoing **Feedback** (bear case) ·
**Interplay: Competitive** with the Bull. Only the stance it argues differs.

### Agent 7 — Research Manager  *(debate facilitator / judge)*

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Role: **Judge + Instructor** · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Communication |
| **2 · World Model** | Agent Awareness: All Agents · Provenance: Communication History · Data Awareness: Full |
| **3 · Observations** | Modality: Text · Context: Whole Environment (full bull/bear history) · Trigger: Communication-Based |
| **4 · Communication** | Incoming: Feedback (both researchers) · Outgoing: **Instruction** (the investment plan) → Trader |
| **5 · Actions** | Type: Writing · CRUD: Create (investment plan; commits to a stance) · Scope: Part of World Model |
| **6 · Interplay** | Cooperative (resolves the Competitive research debate) |

---

## Execution & Risk

### Agent 8 — Trader

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Role: **Recommender** · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Communication |
| **2 · World Model** | Task Awareness: Aware of Others' Tasks · Data Awareness: Full |
| **3 · Observations** | Context: Whole Environment (investment plan + reports) · Trigger: Communication-Based |
| **4 · Communication** | Incoming: Instruction (plan from Research Manager) · Outgoing: **Request** (proposed trade) → Risk debate |
| **5 · Actions** | Type: Writing · CRUD: **Create** (proposed trade: side, size, timing) · Scope: Part of World Model |
| **6 · Interplay** | Cooperative |

### Agents 9–11 — Risk Debate  *(three competing stances on the trade)*

**Shared by all three risk analysts:**

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Role: **Judge** · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Communication |
| **3 · Observations** | Modality: Text · Context: Whole Environment · Trigger: Communication-Based |
| **4 · Communication** | Incoming: Request (Trader's decision) + Feedback (other debators) · Outgoing: **Feedback** (their stance) |
| **5 · Actions** | Type: Writing · CRUD: Create/Update (argument) · Scope: Part of World Model |
| **6 · Interplay** | **Competitive** (three-way) |

**They differ only on the stance they argue:**

| # | Agent | Stance |
|---|-------|--------|
| 9 | Aggressive Risk Analyst | Champions high-reward / high-risk upside |
| 10 | Conservative Risk Analyst | Champions caution / capital preservation |
| 11 | Neutral Risk Analyst | Balances the two extremes |

### Agent 12 — Portfolio Manager  *(risk-debate judge / final decision)*

| Dimension | Details |
|---|---|
| **1 · Configuration** | Type: Software · Role: **Judge + Recommender** · Model: Generative AI · Autonomy: Internal Deliberate · Adaptation: External Communication |
| **2 · World Model** | Agent Awareness: All Agents · Persistence: **Continuous** (portfolio state across runs) · Data Awareness: Full · Provenance: Communication + Action History |
| **3 · Observations** | Modality: Text · Context: Whole Environment (full risk-debate history) · Trigger: Communication-Based |
| **4 · Communication** | Incoming: Feedback (three risk analysts) · Outgoing: **Instruction** (execute final decision) |
| **5 · Actions** | CRUD: **Update** (portfolio: holdings, cash) · Scope: Part of World Model<br>**Delay: Until Action Acknowledged** *(only if human-approval mode is enabled)* |
| **6 · Interplay** | Cooperative (resolves the Competitive risk debate) |

---

## System-level (Dimension 6 — Infrastructure)

- **Initialized Modules:** Configuration · Observation · Action · Communication
- **Dynamic Modules:** Action Module (spawned per analysis / per trade) ·
  **Trigger:** Based on Agents (the Trader's proposal spawns the risk debate) and Based on Environment (new data)
- **Agent Interplay across the system:**
  - **Cooperative** pipeline: Scanner → Analysts → Research Manager → Trader → Portfolio Manager
  - **Competitive** channels: Bull vs Bear (research debate); Aggressive vs Conservative vs Neutral (risk debate)
  - Two **judge** agents resolve the two debates: Research Manager, Portfolio Manager


