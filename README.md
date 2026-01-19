# Rinse Repeat Labs Agent Orchestrator

A command-line tool for coordinating 12 AI agents in virtual meetings for Rinse Repeat Labs, a software development agency.

## Overview

The orchestrator enables **you (the Architect)** to run virtual meetings with AI agents, each representing a distinct role in the company. Agents discuss topics, make decisions, and produce actionable outputs.

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
              │   CEO   │     │   1:1s    │    │  Team     │
              │ Partner │     │  w/Agents │    │ Meetings  │
              └─────────┘     └───────────┘    └───────────┘
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Agent Roster (12 Agents)

### Executive Team
| Agent | Role | Reports To |
|-------|------|------------|
| **CEO** | Vision, strategy, key relationships | Architect |
| **CFO** | Pricing, revenue, financial health | CEO |
| **CITO** | Technical strategy, idea evaluation | CEO |
| **Sales** | Lead management, deals, partnerships | CEO |
| **Legal** | Contracts, compliance, IP | CEO |

### Technical Team
| Agent | Role | Reports To |
|-------|------|------------|
| **DevLead** | Architecture, code quality | CITO |
| **DesignLead** | UI/UX, design systems | CITO |
| **QALead** | Testing, quality, tester program | CITO |

### Operations Team
| Agent | Role | Reports To |
|-------|------|------------|
| **PM** | Project coordination, client comms | CEO |
| **CustomerSuccess** | Post-launch relationships | PM |
| **Marketing** | ASO, growth, brand | CEO |
| **Support** | Tickets, documentation, testers | PM |

## Quick Start

```bash
# Interactive mode (recommended for exploration)
python orchestrator.py interactive

# CEO sync - strategic alignment
python orchestrator.py ceo-sync

# 1:1 with any agent
python orchestrator.py 1on1 --agent cito

# Daily standup with all agents
python orchestrator.py standup

# Company status dashboard
python orchestrator.py status
```

## CLI Commands

### 1:1 Meetings

```bash
# Meet with any agent
python orchestrator.py 1on1 --agent ceo
python orchestrator.py 1on1 --agent cito --topic "Flutter migration"
python orchestrator.py 1on1 --agent cfo --topic "Q1 revenue review"

# Strategic sync with CEO
python orchestrator.py ceo-sync
python orchestrator.py ceo-sync --topic "Q2 hiring plan"
```

### Team Meetings

```bash
# Executive team (CEO, CFO, CITO, Sales, Legal)
python orchestrator.py exec-meeting
python orchestrator.py exec-meeting --topic "New enterprise opportunity"

# Technical team (CITO, DevLead, DesignLead, QALead)
python orchestrator.py tech-meeting
python orchestrator.py tech-meeting --topic "Architecture review"

# Project meeting (PM, DevLead, DesignLead, QALead)
python orchestrator.py project-meeting --project "TimeFlow"
python orchestrator.py project-meeting --project "FitPulse" --topic "Sprint 4"

# All-hands (all 12 agents)
python orchestrator.py all-hands
python orchestrator.py all-hands --topic "Q1 retro and Q2 planning"
```

### Operations

```bash
# Daily standup
python orchestrator.py standup
python orchestrator.py standup --agents "dev_lead,design_lead,qa_lead"

# Review an idea submission
python orchestrator.py idea-review --idea ideas/fitness-app.md

# Project retrospective
python orchestrator.py retro --project "ShopWave"

# Strategy session
python orchestrator.py strategy --topic "Should we adopt Flutter?"

# Custom meeting
python orchestrator.py meeting --topic "Marketing budget" --agents ceo,cfo,marketing
```

### Utilities

```bash
# View recent decisions
python orchestrator.py decisions --last 10
python orchestrator.py decisions --topic "Flutter"

# View past meetings
python orchestrator.py meetings --last 10

# List all agents
python orchestrator.py agents

# Company dashboard
python orchestrator.py status

# Interactive menu
python orchestrator.py interactive
```

## Project Structure

```
rinse-repeat-orchestrator/
├── agents/                  # Agent system prompts (12 files)
│   ├── ceo.md
│   ├── cfo.md
│   ├── cito.md
│   ├── sales.md
│   ├── legal.md
│   ├── dev_lead.md
│   ├── design_lead.md
│   ├── qa_lead.md
│   ├── pm.md
│   ├── customer_success.md
│   ├── marketing.md
│   └── support.md
├── meetings/                # Meeting transcripts (auto-generated)
├── decisions/               # Decision log
│   └── decisions.json
├── context/                 # Shared context for meetings
│   ├── company.md
│   ├── active_projects.md
│   ├── pending_ideas.md
│   └── architect_notes.md
├── src/                     # Source code
│   ├── agent.py
│   ├── meeting.py
│   └── utils.py
├── orchestrator.py          # Main CLI
├── config.py                # Configuration
├── requirements.txt
└── README.md
```

## Meeting Types

| Type | Command | Participants | Purpose |
|------|---------|--------------|---------|
| **1:1** | `1on1` | You + 1 agent | Deep dive on domain |
| **CEO Sync** | `ceo-sync` | You + CEO | Strategic alignment |
| **Executive** | `exec-meeting` | 5 executives | Business decisions |
| **Technical** | `tech-meeting` | 4 tech leads | Architecture, quality |
| **Project** | `project-meeting` | PM + team | Sprint coordination |
| **All-Hands** | `all-hands` | All 12 agents | Company alignment |
| **Standup** | `standup` | All agents | Daily sync |
| **Idea Review** | `idea-review` | 6 agents | Evaluate submissions |
| **Retro** | `retro` | Project team | Lessons learned |
| **Strategy** | `strategy` | Custom | Strategic topics |
| **Custom** | `meeting` | Custom | Any topic |

## Idea Submission Format

Create a markdown file in `context/pending_ideas/`:

```markdown
# App Idea: [Name]

## Submitted By
[Name, email]

## Idea Description
[What is this app?]

## Problem It Solves
[What pain point does it address?]

## Target Users
[Who would use this?]

## Desired Platforms
- [ ] iOS
- [ ] Android
- [ ] Web
- [ ] Desktop

## Preferred Revenue Model
- [ ] Full payment (keep 100%)
- [ ] 70/30 revenue share
- [ ] 50/50 revenue share

## Timeline Expectations
[ASAP / 3 months / 6 months / Flexible]

## Additional Notes
[Anything else relevant]
```

Then run:
```bash
python orchestrator.py idea-review --idea context/pending_ideas/my-idea.md
```

## Configuration

Edit `config.py` to customize:

- `DEFAULT_MODEL`: Claude model to use (default: claude-sonnet-4-20250514)
- `MAX_TOKENS`: Maximum response length
- `MEETING_TYPES`: Default agents and facilitators per meeting type

## Adding New Agents

1. Create a new markdown file in `agents/`:

```markdown
# Agent: [Name]

## Role
[One-line description]

## Expertise
- [Area 1]
- [Area 2]

## Responsibilities
- [Responsibility 1]
- [Responsibility 2]

## Communication Style
[How this agent communicates]

## System Prompt
[Full system prompt for the API]
```

2. Update `config.py` to add the agent to appropriate team lists

## Output

### Meeting Transcripts
Saved to `meetings/YYYY-MM-DD-type-topic.md`:
- Participant list
- Full discussion
- Facilitator synthesis
- Decisions and action items

### Decisions Log
Appended to `decisions/decisions.json`:
- Date, topic, decision
- Rationale and owner
- Status tracking

## Workflow Example

1. **Morning standup**
   ```bash
   python orchestrator.py standup
   ```

2. **New idea arrives** - Create idea file

3. **Review the idea**
   ```bash
   python orchestrator.py idea-review --idea ideas/new-app.md
   ```

4. **Deep dive with CITO**
   ```bash
   python orchestrator.py 1on1 --agent cito --topic "Technical approach"
   ```

5. **Strategic sync with CEO**
   ```bash
   python orchestrator.py ceo-sync --topic "Should we proceed?"
   ```

6. **Check decisions**
   ```bash
   python orchestrator.py decisions --last 5
   ```

## Data Management

The orchestrator includes a complete data management system for tracking business entities:

```bash
# Ideas management
python orchestrator.py ideas list
python orchestrator.py ideas add --name "App Name" --submitter-name "John" --submitter-email "john@example.com" --description "Description"
python orchestrator.py ideas status <id> approved

# Testers management
python orchestrator.py testers list
python orchestrator.py testers add --name "Jane" --email "jane@example.com" --devices "iPhone:14:iOS 17" --payment-method paypal --payment-details "jane@paypal.com"
python orchestrator.py testers approve <id>

# Clients management
python orchestrator.py clients list
python orchestrator.py clients add --name "Contact" --company "Company" --email "contact@company.com"

# Projects management
python orchestrator.py projects list --active

# Finances management
python orchestrator.py finances invoices
python orchestrator.py finances create-invoice --client <id> --project <id> --amount 10000 --description "Milestone 1" --due-date 2026-02-15

# Reports
python orchestrator.py report all
python orchestrator.py ideas report
python orchestrator.py finances report --period 2026-01
```

## Documentation

For detailed information on how the system works:

- **[Architecture Guide](docs/ARCHITECTURE.md)** — System architecture, context sharing, agent interaction patterns
- **[Process Flows](docs/PROCESS.md)** — Idea submission, project lifecycle, decision making, operational processes
- **[Data Management](docs/DATA_MANAGEMENT.md)** — Ideas, testers, clients, projects, finances, and reports

## License

MIT License - See LICENSE file for details.
