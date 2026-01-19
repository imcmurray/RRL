# Rinse Repeat Labs — Architecture & Process Guide

This document explains how the orchestrator works, how agents share context, and the meeting facilitation process.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Context Sharing](#context-sharing)
3. [Agent Interaction Patterns](#agent-interaction-patterns)
4. [Meeting Flow](#meeting-flow)
5. [Decision Tracking](#decision-tracking)
6. [Adding/Modifying Agents](#addingmodifying-agents)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR (CLI)                          │
│  orchestrator.py - Parses commands, coordinates meetings            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │   Meeting   │ │   Agent     │ │   Utils     │
            │  meeting.py │ │  agent.py   │ │  utils.py   │
            └─────────────┘ └─────────────┘ └─────────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌─────────────────────────────────────────────────────────┐
            │                    DATA LAYER                           │
            │  agents/*.md | context/*.md | meetings/*.md | decisions │
            └─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
            ┌─────────────────────────────────────────────────────────┐
            │                  ANTHROPIC API                          │
            │           claude-sonnet-4-20250514 (default)                 │
            └─────────────────────────────────────────────────────────┘
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **CLI** | orchestrator.py | Command parsing, user interaction, menu system |
| **Meeting** | src/meeting.py | Meeting facilitation, transcript generation |
| **Agent** | src/agent.py | Agent loading, API calls, response handling |
| **Utils** | src/utils.py | File I/O, context loading, decision tracking |
| **Config** | config.py | Settings, agent lists, meeting type definitions |

---

## Context Sharing

Context sharing ensures all agents have access to relevant company information during meetings. This creates coherent, informed discussions.

### Context Files

```
context/
├── company.md           # Company overview, services, portfolio
├── active_projects.md   # Current project status and details
├── pending_ideas.md     # Ideas under evaluation
└── architect_notes.md   # Architect's notes and directives
```

### How Context is Injected

```
┌─────────────────────────────────────────────────────────────────────┐
│                        API CALL STRUCTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│  SYSTEM PROMPT                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Agent's System Prompt (from agents/[name].md)                 │  │
│  │ - Role, expertise, responsibilities                           │  │
│  │ - Communication style                                         │  │
│  │ - Behavioral instructions                                     │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ ## Current Context                                            │  │
│  │ - Company info (context/company.md)                           │  │
│  │ - Active projects (context/active_projects.md)                │  │
│  │ - Pending ideas (context/pending_ideas.md) *if relevant*      │  │
│  │ - Extra context (idea content, project focus, etc.)           │  │
│  └───────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  USER MESSAGE                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ ## Prior Discussion in This Meeting                           │  │
│  │ - Previous agents' responses (enables agents to respond to    │  │
│  │   each other and build on prior points)                       │  │
│  ├───────────────────────────────────────────────────────────────┤  │
│  │ Meeting prompt / question                                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Context by Meeting Type

Each meeting type specifies which context to include:

| Meeting Type | Company | Active Projects | Pending Ideas |
|--------------|:-------:|:---------------:|:-------------:|
| 1:1 | ✓ | ✓ | |
| CEO Sync | ✓ | ✓ | ✓ |
| Executive | ✓ | ✓ | |
| Technical | ✓ | ✓ | |
| Project | ✓ | ✓ | |
| All-Hands | ✓ | ✓ | |
| Standup | ✓ | ✓ | |
| Idea Review | ✓ | ✓ | ✓ |
| Retro | ✓ | ✓ | |
| Strategy | ✓ | ✓ | |

### Code Flow

```python
# 1. Meeting determines which context types to load
context_types = ["company", "active_projects"]  # From config.MEETING_TYPES

# 2. Utils loads and combines context files
context = load_context(context_types)
# Returns: company.md content + "---" + active_projects.md content

# 3. Agent.respond() injects context into system prompt
system_prompt = f"{agent.system_prompt}\n\n## Current Context\n\n{context}"

# 4. Prior discussion enables agent-to-agent responses
if prior_discussion:
    message = f"## Prior Discussion\n\n{prior_discussion}\n\n---\n\n{prompt}"
```

---

## Agent Interaction Patterns

### Sequential Discussion

Agents respond in sequence, each seeing prior responses:

```
Meeting Start
    │
    ▼
┌─────────┐
│  CEO    │ ──► Response 1
└─────────┘
    │
    ▼ (CEO's response included in context)
┌─────────┐
│  CFO    │ ──► Response 2 (can reference CEO's points)
└─────────┘
    │
    ▼ (CEO + CFO responses included)
┌─────────┐
│  CITO   │ ──► Response 3 (can reference CEO & CFO)
└─────────┘
    │
    ▼ (All responses included)
┌─────────┐
│  CEO    │ ──► Synthesis (summarizes all input)
└─────────┘
    │
    ▼
Meeting End (transcript saved)
```

### Prior Discussion Format

Each agent receives prior responses formatted as:

```markdown
## Prior Discussion in This Meeting

### CEO
[CEO's full response...]

### CFO
[CFO's full response...]

---

[New prompt for this agent]
```

This enables:
- Building on others' points
- Respectful disagreement
- Cross-functional coordination
- Coherent group discussions

---

## Meeting Flow

### Standard Discussion Meeting

```
1. INITIALIZATION
   ├── Load meeting type config (agents, facilitator, context types)
   ├── Load context files
   └── Display meeting header

2. DISCUSSION PHASE
   ├── For each agent in sequence:
   │   ├── Build prompt with prior discussion
   │   ├── Call Anthropic API
   │   ├── Append response to prior_discussion
   │   └── Display response
   └── All agents have responded

3. SYNTHESIS PHASE
   ├── Facilitator receives all responses
   ├── Generates summary, decisions, action items
   └── Display synthesis

4. OUTPUT PHASE
   ├── Generate markdown transcript
   ├── Save to meetings/YYYY-MM-DD-type-topic.md
   └── Log any decisions to decisions.json
```

### 1:1 Meeting Flow

```
1. INITIALIZATION
   ├── Load agent config
   ├── Load context
   └── Display meeting header

2. RESPONSE
   ├── Agent provides comprehensive update
   └── Display response

3. OUTPUT
   ├── Generate transcript
   └── Save to meetings/
```

### Idea Review Flow

```
1. INITIALIZATION
   ├── Load idea content from file
   ├── Load context + idea as extra context
   └── Select idea review team (CITO, CFO, Sales, Legal, PM, DesignLead)

2. ROLE-SPECIFIC EVALUATION
   ├── CITO: Technical feasibility, stack recommendation
   ├── CFO: Pricing, profitability analysis
   ├── Sales: Client fit, deal potential
   ├── Legal: Contract, compliance, IP
   ├── PM: Timeline, resources
   └── DesignLead: UX complexity

3. SYNTHESIS
   ├── CITO synthesizes all evaluations
   ├── Go/No-Go recommendation
   └── Next steps

4. OUTPUT
   └── Comprehensive evaluation transcript
```

---

## Decision Tracking

Decisions are logged to `decisions/decisions.json`:

```json
{
  "id": 1,
  "date": "2026-01-19",
  "topic": "Technology Strategy",
  "decision": "Adopt Flutter as primary mobile framework",
  "rationale": "Better cross-platform support, team expertise",
  "owner": "DevLead",
  "status": "pending",
  "meeting_type": "tech_meeting"
}
```

### Decision Status Flow

```
pending ──► in_progress ──► completed
```

### Querying Decisions

```bash
# Recent decisions
python orchestrator.py decisions --last 10

# Filter by topic
python orchestrator.py decisions --topic "Flutter"

# Filter by status
python orchestrator.py decisions --status pending

# Filter by owner
python orchestrator.py decisions --owner DevLead
```

---

## Adding/Modifying Agents

### Agent File Structure

```markdown
# Agent: [Display Name]

## Role
[One-line role description]

## Expertise
- [Area 1]
- [Area 2]
- [Area 3]

## Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## Communication Style
[Description of how this agent communicates - tone, approach, style]

## System Prompt
[Full system prompt sent to the API. This is the most important section.
Include:
- Role definition
- Company context reminder
- Meeting behavior guidelines
- Response format preferences
- Domain-specific instructions]
```

### Adding a New Agent

1. **Create the agent file**: `agents/new_agent.md`

2. **Update config.py**:
   ```python
   # Add to ALL_AGENTS
   ALL_AGENTS = [..., "new_agent"]

   # Add to appropriate team
   OPERATIONS_TEAM = [..., "new_agent"]

   # Add display name
   AGENT_DISPLAY_NAMES = {..., "new_agent": "NewAgent"}

   # Add reporting structure
   AGENT_REPORTS_TO = {..., "new_agent": "ceo"}
   ```

3. **Test**: `python orchestrator.py agents`

### Modifying Agent Behavior

Edit the `## System Prompt` section in the agent's markdown file. Key areas to tune:

- **Tone**: More/less formal, technical, friendly
- **Response length**: Verbose vs. concise
- **Focus areas**: What to emphasize
- **Meeting behavior**: How to interact with other agents

---

## Best Practices

### Keeping Context Fresh

1. **Update active_projects.md** regularly with current project status
2. **Add new ideas** to pending_ideas.md before reviews
3. **Use architect_notes.md** for directives agents should follow

### Effective Meetings

1. **Provide specific topics** rather than generic ones
2. **Use appropriate meeting types** for the discussion
3. **Review transcripts** for actual decision-making
4. **Follow up on action items** from synthesis

### Agent Calibration

1. **Run test meetings** to see how agents interact
2. **Tune system prompts** based on response quality
3. **Adjust context** if agents lack necessary information
4. **Balance verbosity** - too long responses slow meetings

---

## API Usage

Each agent turn = 1 API call:

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    system=f"{agent_system_prompt}\n\n## Current Context\n\n{context}",
    messages=[{
        "role": "user",
        "content": f"## Prior Discussion\n\n{prior}\n\n---\n\n{prompt}"
    }]
)
```

### Estimated API Calls per Meeting

| Meeting Type | Agents | Synthesis | Total Calls |
|--------------|--------|-----------|-------------|
| 1:1 | 1 | No | 1 |
| Executive | 5 | Yes | 6 |
| Technical | 4 | Yes | 5 |
| Project | 4 | Yes | 5 |
| All-Hands | 12 | Yes | 13 |
| Standup | 12 | No | 12 |
| Idea Review | 6 | Yes | 7 |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not found | Check agents/*.md file exists and is named correctly |
| Context not loading | Verify context/*.md files exist and have content |
| Incoherent responses | Check prior_discussion is being passed correctly |
| Missing decisions | Ensure decisions/decisions.json is writable |
| API errors | Verify ANTHROPIC_API_KEY is set correctly |
