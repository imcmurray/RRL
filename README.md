# RRL AI Orchestrator

**Run your business with a team of 12 AI agents.** The RRL AI Orchestrator gives you an entire virtual company — CEO, CFO, engineers, designers, marketers, and more — ready to advise, strategize, and help you build.

## Why Use This?

**You're a solo founder** who needs a CFO's perspective on pricing, a lawyer's eye on contracts, and a marketing team's input on launch strategy — but you can't afford a full team.

**You run a small agency** and need consistent processes for evaluating projects, managing clients, and coordinating across functions.

**You want AI that works together**, not just one chatbot. The orchestrator coordinates multiple AI perspectives in meetings, just like a real company.

### What You Get

| Instead of... | You get... |
|---------------|------------|
| $200-500/hr strategic consultant | CEO agent for vision and strategy |
| $150/hr financial advisor | CFO agent for pricing and cash flow |
| $200/hr tech architect | CITO agent for technical decisions |
| Expensive legal review | Legal agent for contract guidance |
| Full dev team salaries | Dev, Design, QA leads for technical perspective |
| Marketing/sales hires | Marketing, Sales, Support agents |

### Three Ways to Work

1. **Chat with the CEO** — Have a conversation, and the CEO can update all your agents, settings, and processes on your behalf
2. **Hold Group Meetings** — Get perspectives from multiple agents at once (Executive team, Technical team, or all 12)
3. **1:1 Deep Dives** — Focus on specific topics with individual agents

```
                            ┌─────────────────┐
                            │    ARCHITECT    │
                            │     (You)       │
                            │  Human Overseer │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
              ┌─────────┐     ┌───────────┐    ┌───────────┐
              │   CEO   │     │   1:1s    │    │  Group    │
              │ Partner │     │  w/Agents │    │ Meetings  │
              └─────────┘     └───────────┘    └───────────┘
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/imcmurray/RRL.git
cd RRL

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Launch the Web Dashboard

```bash
# One command to start (auto-opens browser)
python start.py

# Or run the setup wizard first
python orchestrator.py setup --launch-web
```

### Start Using Your AI Team

**Option 1: Chat with the CEO** (Web)
1. Go to Agent Portals → CEO → Start Chat
2. Tell the CEO what you need: "I want to focus on enterprise clients"
3. The CEO proposes changes → You confirm → All agents updated

**Option 2: Hold a Group Meeting** (Web)
1. Go to Agent Portals → Start Group Meeting
2. Pick a preset (Executive, Technical, All-Hands) or custom agents
3. Type your topic and get perspectives from everyone

**Option 3: CLI Meetings** (Terminal)
```bash
python orchestrator.py ceo-sync                    # Strategic sync with CEO
python orchestrator.py 1on1 --agent cfo            # 1:1 with CFO
python orchestrator.py exec-meeting                # Executive team meeting
python orchestrator.py all-hands --topic "Q1 plan" # All 12 agents
```

## Your AI Team

### Executive Team
| Agent | Role | What They Help With |
|-------|------|---------------------|
| **CEO** | Chief Executive | Vision, strategy, major decisions, company direction |
| **CFO** | Chief Financial | Pricing, cash flow, budgets, financial health |
| **CITO** | Chief Technology | Technical strategy, architecture, tool decisions |
| **Sales** | Sales Director | Lead management, deals, partnerships, revenue |
| **Legal** | Legal Counsel | Contracts, compliance, IP protection |

### Technical Team
| Agent | Role | What They Help With |
|-------|------|---------------------|
| **DevLead** | Development Lead | Architecture, code quality, technical debt |
| **DesignLead** | Design Lead | UI/UX, design systems, accessibility |
| **QALead** | QA Lead | Testing strategy, quality gates, beta programs |

### Operations Team
| Agent | Role | What They Help With |
|-------|------|---------------------|
| **PM** | Project Manager | Timelines, coordination, client communication |
| **CustomerSuccess** | Customer Success | Client health, retention, post-launch support |
| **Marketing** | Marketing Director | Growth, campaigns, ASO, brand |
| **Support** | Support Lead | Tickets, documentation, user issues |

## Features

### Web Dashboard
- **Agent Portals** — Each agent has their own workspace at `/agents/<agent_id>`
- **1:1 Chat** — Real-time conversations with any agent
- **Group Meetings** — Multi-agent discussions with preset or custom groups
- **CEO Management** — Let the CEO update settings and coordinate agents for you
- **Live Updates** — HTMX-powered real-time refresh without page reloads
- **Data Management** — Ideas, clients, projects, testers, finances all in one place

### CLI Interface
```bash
python orchestrator.py ceo-sync                    # Strategic sync with CEO
python orchestrator.py 1on1 --agent cfo            # 1:1 with any agent
python orchestrator.py exec-meeting                # Executive team meeting
python orchestrator.py all-hands --topic "Q1 plan" # All 12 agents
python orchestrator.py interactive                 # Interactive menu
```

### Shared State
CLI and Web Dashboard share the same data files — changes in one appear instantly in the other.

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   CLI Commands  │────▶│  data/*.json files   │◀────│  Web Dashboard  │
│  orchestrator.py│     │  (shared state)      │     │  webapp/app.py  │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
```

## Documentation

For detailed information on how the system works:

- **[User Guide](docs/USER_GUIDE.md)** — Getting started, use case scenarios, dashboard walkthrough, and common workflows
- **[Architecture Guide](docs/ARCHITECTURE.md)** — System architecture, context sharing, agent interaction patterns
- **[Process Flows](docs/PROCESS.md)** — Idea submission, project lifecycle, decision making, operational processes
- **[Data Management](docs/DATA_MANAGEMENT.md)** — Ideas, testers, clients, projects, finances, and reports
- **[Agent Portals](docs/AGENT_PORTALS.md)** — Portal system, feature requests, and agent workspace management

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — Free for personal use, research, education, and non-profits. Commercial use is not permitted.
