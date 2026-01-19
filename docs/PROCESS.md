# Rinse Repeat Labs — Process Flows

This document describes the key operational processes and how agents collaborate.

---

## 1. Idea Submission Flow

When a new client submits an app idea:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         IDEA SUBMISSION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

Client submits idea
        │
        ▼
┌───────────────┐
│    Sales      │ ◄── Acknowledges receipt, gathers missing info
└───────┬───────┘
        │
        ▼ (Creates idea file in context/pending_ideas/)
┌───────────────────────────────────────────────────────────────────────────┐
│                         IDEA REVIEW MEETING                               │
│                                                                           │
│   python orchestrator.py idea-review --idea context/pending_ideas/x.md   │
│                                                                           │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐  ┌────┐ │
│   │  CITO   │  │   CFO   │  │  Sales  │  │  Legal  │  │   PM   │  │Des.│ │
│   │Technical│  │Financial│  │ Client  │  │Contract │  │Timeline│  │ UX │ │
│   │Feasibil.│  │Pricing  │  │  Fit    │  │ Terms   │  │Resource│  │Est.│ │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └───┬────┘  └─┬──┘ │
│        └────────────┴────────────┴────────────┴───────────┴─────────┘    │
│                                    │                                      │
│                                    ▼                                      │
│                           ┌───────────────┐                               │
│                           │ CITO Synthesis│                               │
│                           │ Go / No-Go    │                               │
│                           └───────────────┘                               │
└───────────────────────────────────────────────────────────────────────────┘
        │
        ▼
   ┌─────────┐
   │  Sales  │ ◄── Presents proposal to client
   └────┬────┘
        │
        ▼ (If client accepts)
   ┌─────────┐
   │  Legal  │ ◄── Finalizes contract
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │   PM    │ ◄── Kicks off project
   └─────────┘
```

### Idea Review Evaluation Criteria

| Agent | Evaluates | Key Questions |
|-------|-----------|---------------|
| **CITO** | Technical feasibility | Can we build it? What stack? Risks? |
| **CFO** | Financial viability | Cost to build? Revenue model? Profitable? |
| **Sales** | Client fit | Good client? Market opportunity? |
| **Legal** | Compliance | Regulatory issues? IP concerns? Contract terms? |
| **PM** | Delivery | Timeline? Resources needed? Capacity? |
| **DesignLead** | UX complexity | Design effort? User research needed? |

### Idea File Template

```markdown
# App Idea: [Name]

## Submitted By
[Name, email, company]

## Idea Description
[What is this app? What does it do?]

## Problem It Solves
[What pain point does it address?]

## Target Users
[Who would use this? Demographics, behaviors]

## Desired Platforms
- [ ] iOS
- [ ] Android
- [ ] Web
- [ ] Desktop (Windows/macOS/Linux)

## Key Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Competitors
[Existing solutions in the market]

## Differentiation
[What makes this unique?]

## Preferred Revenue Model
- [ ] Full payment (client keeps 100% revenue)
- [ ] 70/30 revenue share (reduced upfront)
- [ ] 50/50 revenue share (minimal upfront)

## Timeline Expectations
[ASAP / 3 months / 6 months / Flexible]

## Budget Range (Optional)
[If willing to share]

## Additional Notes
[Anything else relevant]
```

---

## 2. Project Lifecycle

Once a project is approved and contracted:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PROJECT LIFECYCLE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Project Kickoff
        │
        ▼
┌───────────────┐
│      PM       │ ◄── Creates project plan, sets up communication
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  DesignLead   │ ◄── Wireframes, prototypes, design system
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   DevLead     │ ◄── Architecture, implementation
└───────┬───────┘     (Multiple sprints with PM coordination)
        │
        ▼
┌───────────────┐
│   QALead      │ ◄── Testing, bug triage, release sign-off
└───────┬───────┘
        │
        ▼
┌───────────────┐
│      PM       │ ◄── Coordinates launch
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Marketing    │ ◄── Launch promotion, ASO
└───────┬───────┘
        │
        ▼
┌───────────────────────┐
│   CustomerSuccess     │ ◄── Ongoing relationship
└───────────┬───────────┘
            │
            ▼
┌───────────────┐
│    Support    │ ◄── Handles tickets, documentation
└───────────────┘
```

### Project Meetings

| Phase | Meeting Type | Frequency | Participants |
|-------|--------------|-----------|--------------|
| Planning | Project Meeting | Start | PM, CITO, DevLead, DesignLead, QALead |
| Sprint | Project Meeting | Weekly | PM, DevLead, DesignLead, QALead |
| Daily | Standup | Daily | Project team |
| Pre-launch | Tech Meeting | Once | CITO, DevLead, QALead |
| Post-launch | Retro | Once | Full project team |

---

## 3. Daily Operations

### Morning Standup

```bash
python orchestrator.py standup
```

All 12 agents report:
- **Done:** What they completed
- **Doing:** Current focus
- **Blocked:** Any issues

### Weekly Rhythm

| Day | Activity |
|-----|----------|
| Monday | All-hands or CEO sync to set priorities |
| Daily | Standups |
| As needed | Project meetings, tech meetings |
| Friday | Review decisions, update project status |

---

## 4. Decision Making

### Decision Types & Authority

| Decision Type | Recommends | Decides | Approves |
|---------------|------------|---------|----------|
| Technical architecture | DevLead | CITO | — |
| Technology stack | CITO | CITO | CEO (if major) |
| Project pricing | CFO + Sales | CFO | CEO |
| Contract terms | Legal + Sales | Legal | CEO |
| Project timeline | PM + CITO | PM | CEO (if major) |
| Hire/contractor | CEO | CEO | Architect |
| New partnership | CEO + Sales | CEO | Architect |
| Major pivot | CEO | CEO | Architect |
| Client acceptance | Sales | Sales | CEO |
| Launch readiness | QALead + PM | CITO | — |

### Decision Flow

```
Issue identified
        │
        ▼
Relevant agent(s) analyze
        │
        ▼
Recommendation prepared
        │
        ▼
Meeting discussion (if needed)
        │
        ▼
Decision made by authority
        │
        ▼
Logged to decisions.json
        │
        ▼
Action items assigned
        │
        ▼
Follow-up tracked
```

---

## 5. Tester Program Flow

```
Applicant applies (via website)
        │
        ▼
┌───────────────┐
│    QALead     │ ◄── Reviews application, checks devices, approves/rejects
└───────┬───────┘
        │
        ▼ (If approved)
┌───────────────┐
│    Support    │ ◄── Onboards tester, explains process
└───────┬───────┘
        │
        ▼ (When project needs testing)
┌───────────────┐
│    QALead     │ ◄── Assigns testers to project
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    Support    │ ◄── Coordinates feedback, answers questions
└───────┬───────┘
        │
        ▼ (Testing complete)
┌───────────────┐
│     CFO       │ ◄── Processes tester payments
└───────────────┘
```

---

## 6. Escalation Paths

### Technical Issues
```
Support → DevLead → CITO → CEO → Architect
```

### Client Issues
```
Support → CustomerSuccess → PM → Sales → CEO → Architect
```

### Financial Issues
```
PM → CFO → CEO → Architect
```

### Legal Issues
```
Sales/PM → Legal → CEO → Architect
```

---

## 7. Context Updates

Keep context files current for informed agent responses:

### active_projects.md

Update when:
- New project starts
- Project status changes (kickoff → development → QA → launch)
- Blockers arise or resolve
- Milestones reached

```markdown
## [Project Name]
- **Status:** [Kickoff/Development/QA/Launch/Maintenance]
- **Client:** [Client name]
- **PM Notes:** [Current status, key info]
- **Blockers:** [Any blockers, or "None"]
```

### pending_ideas.md

Update when:
- New idea submitted
- Idea reviewed (add outcome)
- Idea moves to project (remove)

### architect_notes.md

Update with:
- Strategic directives
- Process changes
- Focus areas for agents
- Temporary priorities

---

## 8. Retrospective Process

After project completion:

```bash
python orchestrator.py retro --project "ProjectName"
```

### Retro Format

Each agent shares:
1. **What went well** — Successes to repeat
2. **What didn't go well** — Pain points and issues
3. **Lessons learned** — Takeaways for future
4. **Action items** — Specific improvements

### Retro Participants

| Agent | Focus Area |
|-------|------------|
| PM | Process, coordination, client relationship |
| DevLead | Technical execution, code quality |
| DesignLead | Design process, user feedback |
| QALead | Testing effectiveness, bug rates |
| CITO | Architecture decisions, tech choices |

---

## 9. Strategic Planning

### CEO Sync (Architect + CEO)

```bash
python orchestrator.py ceo-sync --topic "Q2 Strategy"
```

For:
- Vision alignment
- Business health review
- Major decisions
- Direction setting

### Executive Meeting (C-Suite)

```bash
python orchestrator.py exec-meeting --topic "Growth Strategy"
```

For:
- Cross-functional executive alignment
- Major business decisions
- Resource allocation
- Partnership discussions

### All-Hands

```bash
python orchestrator.py all-hands --topic "Company Update"
```

For:
- Company-wide communication
- Major announcements
- Celebrating wins
- Addressing challenges

---

## 10. Metrics & Reporting

### Agent Metrics

| Agent | Key Metrics |
|-------|-------------|
| CEO | Revenue, client count, team health |
| CFO | Profit margin, cash flow, AR/AP aging |
| CITO | Tech debt score, idea conversion rate |
| Sales | Pipeline value, conversion rate, deal velocity |
| Legal | Contract turnaround time, compliance status |
| DevLead | Code quality metrics, velocity, bug rate |
| DesignLead | Design consistency, user satisfaction scores |
| QALead | Bug escape rate, test coverage, release quality |
| PM | On-time delivery %, scope creep, client satisfaction |
| CustomerSuccess | NPS, retention rate, expansion revenue |
| Marketing | App rankings, traffic, conversion rates |
| Support | Response time, resolution rate, satisfaction |

### Status Dashboard

```bash
python orchestrator.py status
```

Shows:
- Active agent count
- Recent meetings
- Recent decisions
- Overall health snapshot
