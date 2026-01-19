# Agent Portals

Each of the 12 AI agents in the Rinse Repeat Labs orchestrator has a dedicated portal in the web dashboard. These portals allow agents to manage their workspace and request new features, just like employees in a real company.

## Overview

Agent portals serve two key purposes:

1. **Workspace Management** — Each agent has a customized view of their responsibilities, metrics, and relevant data
2. **Feature Requests** — Agents can request new tools, data, or improvements to their section of the dashboard

This creates a self-improving system where agents can identify their own needs and the Architect (human overseer) can prioritize and implement the most valuable changes.

## Accessing Agent Portals

### Web Dashboard

Start the Flask web application:

```bash
cd webapp
python app.py
```

Navigate to:
- **All Portals:** `http://localhost:5000/agents`
- **Individual Portal:** `http://localhost:5000/agents/<agent_id>`

Agent IDs: `ceo`, `cfo`, `cito`, `sales`, `legal`, `dev_lead`, `design_lead`, `qa_lead`, `pm`, `customer_success`, `marketing`, `support`

### CLI Access

```bash
# List all feature requests
python orchestrator.py requests list

# View pending requests
python orchestrator.py requests pending

# Show a specific request
python orchestrator.py requests show <request_id>
```

## Portal Components

### Agent Profile

Each portal displays:
- **Role & Name** — Agent's title and full name
- **Description** — What the agent does
- **Team** — Executive, Technical, or Operations
- **Responsibilities** — Key duties
- **Metrics** — Performance indicators they track

### Feature Requests

Agents can view and manage their submitted requests:
- **Total Requests** — All requests submitted
- **Pending** — Awaiting review
- **Approved** — Ready for implementation
- **Implemented** — Completed and deployed

### Recent Activity

Timeline of recent actions and request status changes.

## Feature Request System

### Request Types

| Type | Description | Examples |
|------|-------------|----------|
| **Feature** | New functionality | Dashboard widgets, new tools |
| **Enhancement** | Improvements to existing features | Better filtering, faster loading |
| **Data/Report** | New metrics, dashboards, reports | KPI tracking, trend analysis |
| **Integration** | External system connections | API integrations, third-party tools |
| **UI/UX** | Interface improvements | Better layouts, clearer navigation |
| **Automation** | Automated workflows | Alerts, scheduled reports, reminders |

### Priority Levels

| Priority | Description | Use When |
|----------|-------------|----------|
| **Critical** | Blocking current work | Can't perform essential duties |
| **High** | Significantly impacts effectiveness | Major productivity improvement |
| **Medium** | Would improve workflow | Moderate benefit (default) |
| **Low** | Nice to have | Minor convenience |

### Request Workflow

```
┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌─────────────┐     ┌─────────────┐
│ Submit   │────▶│ Under Review│────▶│ Approved │────▶│ In Progress │────▶│ Implemented │
└──────────┘     └─────────────┘     └──────────┘     └─────────────┘     └─────────────┘
                        │
                        │
                        ▼
                 ┌──────────┐
                 │ Rejected │
                 └──────────┘
                        │
                        ▼
                 ┌──────────┐
                 │ Deferred │
                 └──────────┘
```

1. **Submitted** — Request created by agent
2. **Under Review** — Architect is evaluating
3. **Approved** — Request accepted, awaiting implementation
4. **Rejected** — Request declined (with reason)
5. **Deferred** — Postponed for later consideration
6. **In Progress** — Currently being implemented
7. **Implemented** — Complete and deployed

### Agent Voting

Other agents can vote on requests:
- **Support** — Indicates the feature would help them too
- **Oppose** — Indicates concerns about the request

Votes help the Architect understand cross-team impact and prioritize effectively.

## CLI Commands

### Listing Requests

```bash
# All requests
python orchestrator.py requests list

# Filter by agent
python orchestrator.py requests list --agent ceo

# Filter by status
python orchestrator.py requests list --status approved

# Limit results
python orchestrator.py requests list --limit 10
```

### Viewing Requests

```bash
# Show pending requests (prioritized)
python orchestrator.py requests pending

# Show specific request details
python orchestrator.py requests show <request_id>
```

### Creating Requests

```bash
# Create a feature request
python orchestrator.py requests create \
  --agent ceo \
  --title "Revenue Dashboard" \
  --description "Real-time dashboard showing revenue by project and client" \
  --type feature \
  --priority high \
  --justification "Need visibility into financial performance for strategic decisions" \
  --area "Dashboard"
```

### Managing Requests (Architect)

```bash
# Approve a request
python orchestrator.py requests approve <request_id> \
  --note "Great idea, adding to next sprint"

# Reject a request
python orchestrator.py requests reject <request_id> \
  --reason "Duplicates existing functionality"

# Update status
python orchestrator.py requests status <request_id> in_progress \
  --note "Development started"

# Cast a vote (as another agent)
python orchestrator.py requests vote <request_id> cfo --type support
```

## Best Practices

### For Agents

When submitting requests:

1. **Be Specific** — Clearly describe what you need
2. **Explain the Why** — Include business justification
3. **Consider Impact** — Think about how it affects other agents
4. **Set Realistic Priority** — Reserve "critical" for true blockers
5. **Suggest Solutions** — Include ideas for implementation

Example of a good request:
```
Title: Client Health Score Dashboard

Description: A dashboard showing client health scores based on:
- Project delivery status
- Payment history
- Support ticket trends
- NPS/satisfaction scores

Justification: Currently I have to manually check multiple systems
to assess client health. An aggregated view would save 2-3 hours
weekly and help identify at-risk clients before issues escalate.

Type: Data/Report
Priority: High
Affected Area: CustomerSuccess Dashboard
```

### For the Architect

When reviewing requests:

1. **Consider Cross-Team Value** — Look at votes from other agents
2. **Batch Related Requests** — Implement related features together
3. **Provide Feedback** — Always explain approval/rejection decisions
4. **Track Patterns** — Repeated requests indicate real needs
5. **Balance Teams** — Ensure all teams get attention

## Agent-Specific Portals

### Executive Team

| Agent | Portal Focus |
|-------|-------------|
| **CEO** | Strategic metrics, company health, key relationships |
| **CFO** | Financial dashboards, invoicing, cash flow |
| **CITO** | Technical evaluation, architecture decisions, team metrics |
| **Sales** | Pipeline management, lead tracking, deal velocity |
| **Legal** | Contract tracking, compliance status, NDA management |

### Technical Team

| Agent | Portal Focus |
|-------|-------------|
| **DevLead** | Code quality, sprint velocity, technical debt |
| **DesignLead** | Design assets, user research, accessibility |
| **QALead** | Test coverage, bug metrics, release readiness |

### Operations Team

| Agent | Portal Focus |
|-------|-------------|
| **PM** | Project status, resource allocation, delivery metrics |
| **CustomerSuccess** | Client health, NPS, retention metrics |
| **Marketing** | Growth metrics, ASO rankings, campaign performance |
| **Support** | Ticket volume, response times, knowledge base |

## Data Storage

Feature requests are stored in `data/agent_requests.json` with the following structure:

```json
{
  "id": "uuid",
  "agent_id": "ceo",
  "title": "Request Title",
  "description": "Detailed description",
  "request_type": "feature",
  "priority": "medium",
  "status": "submitted",
  "justification": "Business justification",
  "affected_area": "Dashboard section",
  "votes": {
    "support": ["cfo", "sales"],
    "oppose": []
  },
  "review_notes": [],
  "created_at": "2026-01-19T12:00:00",
  "reviewed_at": null,
  "reviewed_by": null
}
```

## Integration with Meetings

Agents are aware of their portal capabilities during meetings. When an agent identifies a need for new functionality, they can:

1. Mention it in the meeting for discussion
2. Submit a formal request through their portal
3. Get feedback from other agents (votes)
4. Track implementation progress

This creates a feedback loop where meeting discussions can drive portal improvements, and portal analytics can inform meeting discussions.
