# Rinse Repeat Labs Agent Orchestrator

A command-line orchestrator that coordinates multiple AI agents for virtual meetings, enabling collaborative discussions, decision-making, and actionable outputs.

## Overview

The orchestrator enables "virtual meetings" where AI agents (each with a distinct role and persona) discuss topics, make decisions, and produce structured outputs. It's designed for Rinse Repeat Labs, a software development agency that uses Claude-powered agents to run the company.

## Agents

The orchestrator includes six specialized agents:

| Agent | Role |
|-------|------|
| **CITO** | Chief Information Technology Officer — Technical strategy, idea evaluation |
| **PM** | Project Manager — Sprint planning, coordination, client communication |
| **DevLead** | Lead Developer — Architecture, code quality, implementation decisions |
| **QALead** | QA Lead — Test planning, bug triage, release sign-off |
| **CustomerSuccess** | Customer Success Manager — Post-launch support, client satisfaction |
| **Marketing** | Marketing/Growth Lead — ASO, launch strategy, analytics |

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rinse-repeat-orchestrator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

## Usage

### Quick Start

```bash
# Run in interactive mode (recommended for exploration)
python orchestrator.py interactive

# Run a standup with all agents
python orchestrator.py standup

# Get help
python orchestrator.py --help
```

### Meeting Types

#### Daily Standup
Quick status sync where each agent reports what they've done, what they're doing, and any blockers.

```bash
python orchestrator.py standup
python orchestrator.py standup --agents cito,pm,dev_lead
```

#### Strategy Session
Deep discussion on a specific topic with synthesis and action items.

```bash
python orchestrator.py strategy --topic "Q2 hiring plan"
python orchestrator.py strategy --topic "Should we adopt Flutter?" --agents cito,dev_lead,qa_lead
```

#### Idea Review
Comprehensive evaluation of a new idea or proposal.

```bash
python orchestrator.py idea-review --idea path/to/proposal.md
```

#### Project Retrospective
Review a completed project: what went well, what didn't, and lessons learned.

```bash
python orchestrator.py retro --project "TimeFlow"
```

#### Custom Meeting
Free-form discussion on any topic.

```bash
python orchestrator.py meeting --topic "Any topic you want to discuss"
python orchestrator.py meeting --topic "API versioning strategy" --agents dev_lead,qa_lead
```

### Viewing Data

```bash
# View recent decisions
python orchestrator.py decisions --last 10
python orchestrator.py decisions --status pending --owner DevLead

# View past meetings
python orchestrator.py meetings --last 5

# List available agents
python orchestrator.py agents
```

### Interactive Mode

The interactive mode provides a menu-driven interface for easier exploration:

```bash
python orchestrator.py interactive
```

```
Rinse Repeat Labs — Agent Orchestrator

What would you like to do?
  1. Run a standup
  2. Strategy session
  3. Review an idea
  4. Project retrospective
  5. Custom meeting
  6. View past meetings
  7. View decisions
  8. List agents
  9. Exit
```

## Project Structure

```
rinse-repeat-orchestrator/
├── agents/                    # Agent persona definitions
│   ├── cito.md
│   ├── pm.md
│   ├── dev_lead.md
│   ├── qa_lead.md
│   ├── customer_success.md
│   └── marketing.md
├── meetings/                  # Generated meeting transcripts
│   └── [YYYY-MM-DD-type-topic].md
├── decisions/                 # Decision tracking
│   └── decisions.json
├── context/                   # Shared context files
│   ├── company.md            # Company overview
│   ├── active_projects.md    # Current projects
│   └── pending_ideas.md      # Ideas under evaluation
├── src/                       # Source code
│   ├── __init__.py
│   ├── agent.py              # Agent class
│   ├── meeting.py            # Meeting facilitation
│   └── utils.py              # Utility functions
├── config.py                  # Configuration
├── orchestrator.py            # Main CLI
├── requirements.txt           # Dependencies
└── README.md
```

## Configuration

Edit `config.py` to customize:

- `DEFAULT_MODEL`: Claude model to use (default: `claude-sonnet-4-20250514`)
- `MAX_TOKENS`: Maximum tokens per response
- `DEFAULT_AGENTS`: Default agents for meetings
- `MEETING_TYPES`: Meeting type configurations

## Adding New Agents

1. Create a new markdown file in `agents/`:

```markdown
# Agent: NewAgent

## Role
One-line role description

## Expertise
- Area 1
- Area 2

## Responsibilities
- Responsibility 1
- Responsibility 2

## Communication Style
How this agent communicates

## System Prompt
Full system prompt for the API...
```

2. Update `config.py` to add the agent to `DEFAULT_AGENTS` and `AGENT_DISPLAY_NAMES` if desired.

## Output Format

### Meeting Transcript

Meeting transcripts are saved as markdown files in the `meetings/` directory:

```markdown
# Strategy Session: Q2 Technology Investments
**Date:** 2026-01-19
**Participants:** CITO, PM, DevLead, QALead
**Facilitator:** CITO

---

## Discussion

### CITO
[Agent's response...]

### DevLead
[Agent's response...]

---

## Synthesis (by CITO)
[Summary, decisions, action items...]
```

### Decisions

Decisions are logged to `decisions/decisions.json`:

```json
[
  {
    "id": 1,
    "date": "2026-01-19",
    "topic": "Technology Strategy",
    "decision": "Adopt Flutter as primary mobile framework",
    "rationale": "Better cross-platform support",
    "owner": "DevLead",
    "status": "pending"
  }
]
```

## API Usage

The orchestrator uses the Anthropic API. Each agent turn makes one API call:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    system=agent.system_prompt + shared_context,
    messages=[{"role": "user", "content": meeting_prompt}]
)
```

## License

MIT License
