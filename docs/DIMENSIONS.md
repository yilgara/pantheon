# Design-Space Dimensions — Plain-English Reference

This is a cheat sheet for the vocabulary used in [`ROLES.md`](ROLES.md), so you can
read the agent specs **without** opening the paper. Every agent is described along
six dimensions; each dimension has a few possible values, explained below in one line.

Source vocabulary: Stähle et al., *"A Design Space for Intelligent Agents in
Mixed-Initiative Visual Analytics"* (arXiv:2512.23372).

---

## How to read an agent entry

Each agent lists a value for the six dimensions. Think of them as answering six
questions:

1. **Configuration & Logic** — *What is this agent, and how does it think?*
2. **World Model** — *What does it know and remember?*
3. **Observations** — *What does it perceive, and when?*
4. **Communication** — *How does it talk to other agents?*
5. **Actions** — *What can it do, and to what?*
6. **Infrastructure** — *How does it fit into the overall system?*

---

## 1. Configuration & Logic — *what the agent is*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **Type** | Human | A real person is this agent. |
| | Wizard | A person *pretending* to be the AI (a research technique). |
| | Software | A program / LLM. |
| **Role** | Analyzer | Interprets data and draws conclusions. |
| | Instructor | Tells other agents what to do. |
| | Interactor | Handles back-and-forth interaction (esp. with a human). |
| | Recommender | Proposes an action or choice. |
| | Explorer | Searches / browses to find things. |
| | Visualizer | Produces charts or visual output. |
| | Generator | Creates new content (text, options, candidates). |
| | Ranker | Orders items by some criterion. |
| | Judge | Evaluates, critiques, or decides between options. |
| | Summarizer | Condenses lots of input into a short form. |
| | Labeler | Tags or categorizes items. |
| **Model Type** | Rule-Based | Fixed logic / heuristics, no learning. |
| | Generative AI | An LLM (what most of our agents are). |
| | Supervised / Unsupervised / RL | Classic ML training styles. |
| | Human Brain | The agent is a person. |
| **Autonomy** | Internal Deliberate | Acts on its own, after reasoning. |
| | Internal Spontaneous | Acts on its own, reactively / without deliberation. |
| | External | Only acts when something outside triggers it. |
| **Adaptation** | Internal | Changes its own behavior over time. |
| | External Observations | Adapts based on what it observes. |
| | External Communication | Adapts based on messages from others. |
| | None | Doesn't adapt. |

## 2. World Model — *what the agent knows & remembers*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **Provenance Tracking** | Observation History | Remembers what it saw. |
| | Action History | Remembers what it did. |
| | Interaction History | Remembers its interactions. |
| | Communication History | Remembers messages exchanged. |
| | None | Keeps no history. |
| **Persistence** | Continuous | Memory lasts across runs (e.g. the portfolio). |
| | Session-Based | Memory lasts one run, then resets. |
| | Not Persistent | No memory between steps. |
| **Data Awareness** | Full | Sees all the data. |
| | Aligns with Observations | Only knows what it observed. |
| | Subpart of Observation | Sees only a slice. |
| **Agent Awareness** | Aware of all Agents | Knows every other agent exists. |
| | Aware of a Subset | Knows some others. |
| | Not Aware of Others | Thinks it's alone. |
| **Task Awareness** | Self Aware | Knows its own task. |
| | Aware of Others' Tasks | Knows what others are doing. |
| | No Awareness | Doesn't track tasks. |

## 3. Observations — *what the agent perceives, and when*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **Data Structure** | Structured | Clean tables / numbers. |
| | Semi-Structured | Partly organized (e.g. JSON, tagged text). |
| | Unstructured | Free text, raw content. |
| **Sensor Modality** | Text | Reads text. |
| | Numeric | Reads numbers. |
| | Visual | Reads images / charts. |
| | Code | Reads / runs code. |
| **Context Level** | One Input | Looks at a single item. |
| | Multiple Inputs | Looks at several items. |
| | Whole Environment | Looks at everything available. |
| **Synchronism** | Synchronized | Perceives in lockstep with the system. |
| | Asynchronized | Perceives on its own schedule. |
| **Trigger** | Internal | Decides on its own when to observe. |
| | Communication-Based | Observes when messaged. |
| | Infrastructure-Based | Observes when the system tells it to. |

## 4. Communication — *how the agent talks to others*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **Payload** | Signal | Sends a bare notification (no data). |
| | Signal + Data | Sends a message *with* content. |
| | None | Doesn't send anything. |
| **Type (Outgoing/Incoming)** | Notification | "Here's an update / a result." |
| | Instruction | "Do this." |
| | Request | "Please do / decide something." |
| | Feedback | "Here's my judgment / critique." |
| | Availability | "I'm ready / here." |
| | None | No message of that direction. |
| **Internal Sharing** | Operational Sharing | Shares working state. |
| | World Model Sharing | Shares its knowledge/memory. |
| | None | Shares nothing. |
| **Trigger** | Internal / Context-Based / Communication-Based / Infrastructure-Based | *When* it sends — on its own, based on context, when messaged, or when the system says. |

## 5. Actions — *what the agent can do, and to what*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **CRUD Type** | Create | Makes something new. |
| | Update | Changes something. |
| | Delete | Removes something. |
| **Type** | Writing | Produces text (reports, arguments). |
| | Counting | Computes / tallies numbers. |
| | Coding | Writes or runs code. |
| | Visualizing | Makes visuals. |
| | Interacting | Acts through interaction (clicks, inputs). |
| **Affected Scope** | Entire Environment | Changes the whole system. |
| | Part of World Model | Changes a piece of the shared state. |
| | Outside of World Model | Acts on something external. |
| **Trigger** | Internal / Context-Based / Communication-Based | *When* it acts. |
| **Delay** | No Delay | Acts immediately. |
| | Static Duration | Waits a fixed time. |
| | Metric-Based | Waits until some measure is met. |
| | **Until Acknowledged** | Waits for another agent (or a human) to approve — our human-approval gate. |

## 6. Infrastructure — *how agents fit into the system*

| Attribute | Value | Plain meaning |
|-----------|-------|---------------|
| **Initialized Modules** | Configuration / Observation / Action / Communication | Which capabilities exist from the start. |
| **Dynamic Modules** | (same four) / None | Which capabilities get created on the fly. |
| **Trigger of Dynamic Modules** | Planned Time Steps / Based on Agents / Based on Environment / None | *What* causes new modules to spin up. |
| **Agent Interplay** | Independent | Agents don't affect each other. |
| | Cooperative | Agents work together toward a goal. |
| | Competitive | Agents argue / oppose each other (our debates). |

---

## The three that matter most for Pantheon

If you only remember a few, remember these — they're the ones that carry Pantheon's story:

- **Role** (dim 1) — the agent's *job* (Analyzer, Judge, Recommender, Explorer/Ranker…).
- **Agent Interplay** (dim 6) — **Cooperative** vs **Competitive**; our two debates are the Competitive parts.
- **Delay: Until Acknowledged** (dim 5) — the hook for the optional human-approval gate (mixed-initiative).
