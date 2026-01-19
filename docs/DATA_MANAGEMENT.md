# Rinse Repeat Labs — Data Management Guide

This document explains the data management system for tracking ideas, testers, clients, projects, and finances.

---

## Overview

The orchestrator includes a structured data management system stored in JSON files under the `data/` directory. This enables:

- **Persistent storage** of business entities
- **Querying and filtering** records
- **Report generation** for each entity type
- **Communication tracking** with external parties
- **Financial management** and invoicing

---

## Data Directory Structure

```
data/
├── ideas.json       # App idea submissions
├── testers.json     # Beta tester program
├── clients.json     # Client relationships
├── projects.json    # Development projects
└── finances.json    # Invoices, payments, revenue shares

reports/             # Generated reports (auto-created)
├── YYYY-MM-DD-ideas-pipeline.md
├── YYYY-MM-DD-tester-program.md
├── YYYY-MM-DD-projects-status.md
└── YYYY-MM-DD-financial-summary.md

templates/
├── emails/          # Email templates
│   ├── idea_received.md
│   ├── idea_approved.md
│   ├── idea_declined.md
│   ├── tester_welcome.md
│   └── tester_assignment.md
└── reports/         # Report templates
```

---

## Ideas Management

### CLI Commands

```bash
# List all ideas
python orchestrator.py ideas list
python orchestrator.py ideas list --status submitted
python orchestrator.py ideas list --status approved

# Add a new idea
python orchestrator.py ideas add \
  --name "FitTracker App" \
  --description "AI-powered fitness tracking" \
  --submitter-name "John Smith" \
  --submitter-email "john@example.com" \
  --company "FitCo Inc" \
  --platforms "iOS,Android" \
  --revenue-model "70_30" \
  --timeline "3 months"

# Show idea details
python orchestrator.py ideas show <idea_id>

# Update idea status
python orchestrator.py ideas status <idea_id> under_review
python orchestrator.py ideas status <idea_id> approved --note "Great fit for our portfolio"

# Generate ideas report
python orchestrator.py ideas report
python orchestrator.py ideas report --id <idea_id>  # Detailed single idea
```

### Idea Statuses

| Status | Description |
|--------|-------------|
| `submitted` | New submission, awaiting review |
| `under_review` | Currently being evaluated |
| `approved` | Approved for development |
| `rejected` | Not a good fit |
| `in_development` | Active project |
| `completed` | Project finished |
| `on_hold` | Paused |

### Idea Data Schema

```json
{
  "id": "abc12345",
  "name": "App Name",
  "description": "Full description",
  "submitter": {
    "name": "Contact Name",
    "email": "email@example.com",
    "company": "Company Name"
  },
  "platforms": ["iOS", "Android", "Web"],
  "revenue_model": "70_30",
  "timeline": "3 months",
  "budget_range": "$50k-100k",
  "features": ["Feature 1", "Feature 2"],
  "competitors": "Competitor analysis",
  "differentiation": "Unique value prop",
  "status": "submitted",
  "review": {
    "date": "2026-01-19T10:00:00",
    "recommendation": "GO",
    "confidence": "High",
    "tech_assessment": {...},
    "financial_assessment": {...},
    "timeline_estimate": "4-5 months",
    "concerns": ["Concern 1"],
    "next_steps": ["Step 1"]
  },
  "communications": [...],
  "notes": [...],
  "created_at": "2026-01-19T10:00:00",
  "updated_at": "2026-01-19T10:00:00"
}
```

---

## Testers Management

### CLI Commands

```bash
# List all testers
python orchestrator.py testers list
python orchestrator.py testers list --status active
python orchestrator.py testers list --device iPhone

# Add a new tester
python orchestrator.py testers add \
  --name "Jane Doe" \
  --email "jane@example.com" \
  --devices "iPhone:14 Pro:iOS 17,Android:Pixel 7:Android 14" \
  --experience experienced \
  --hours 10 \
  --payment-method paypal \
  --payment-details "jane@paypal.com"

# Approve/reject applications
python orchestrator.py testers approve <tester_id> --note "Great device coverage"
python orchestrator.py testers reject <tester_id> --reason "No Android devices"

# Assign to project
python orchestrator.py testers assign <tester_id> <project_id>

# Generate report
python orchestrator.py testers report
```

### Tester Statuses

| Status | Description |
|--------|-------------|
| `applied` | Application submitted |
| `approved` | Approved, awaiting assignment |
| `active` | Currently testing a project |
| `inactive` | Not currently assigned |
| `rejected` | Application rejected |

### Tester Data Schema

```json
{
  "id": "tst12345",
  "name": "Tester Name",
  "email": "tester@example.com",
  "devices": [
    {"type": "iPhone", "model": "14 Pro", "os": "iOS 17"},
    {"type": "Android", "model": "Pixel 7", "os": "Android 14"}
  ],
  "experience_level": "experienced",
  "hours_per_week": 10,
  "payment": {
    "method": "paypal",
    "details": "email@paypal.com"
  },
  "location": "USA",
  "languages": ["English", "Spanish"],
  "status": "active",
  "projects": ["proj123", "proj456"],
  "feedback_count": 45,
  "total_earned": 350.00,
  "rating": 4.5,
  "communications": [...],
  "notes": [...]
}
```

---

## Clients Management

### CLI Commands

```bash
# List all clients
python orchestrator.py clients list

# Add a new client
python orchestrator.py clients add \
  --name "John Smith" \
  --company "Acme Corp" \
  --email "john@acme.com" \
  --phone "+1-555-1234" \
  --source "Website form"

# Show client details
python orchestrator.py clients show <client_id>

# Generate client report
python orchestrator.py clients report <client_id>
```

### Client Data Schema

```json
{
  "id": "cli12345",
  "name": "Contact Name",
  "company": "Company Name",
  "email": "contact@company.com",
  "phone": "+1-555-1234",
  "address": "123 Main St",
  "billing_email": "billing@company.com",
  "primary_contact": "Contact Name",
  "source": "Website form",
  "projects": ["proj123"],
  "ideas": ["idea456"],
  "total_revenue": 75000.00,
  "total_invoiced": 80000.00,
  "total_paid": 75000.00,
  "status": "active",
  "communications": [...],
  "notes": [...]
}
```

---

## Projects Management

### CLI Commands

```bash
# List all projects
python orchestrator.py projects list
python orchestrator.py projects list --active
python orchestrator.py projects list --status development

# Generate projects report
python orchestrator.py projects report
```

### Project Statuses

| Status | Description |
|--------|-------------|
| `planning` | Initial planning phase |
| `design` | UI/UX design phase |
| `development` | Active development |
| `qa` | Testing and QA |
| `launch` | Preparing for launch |
| `maintenance` | Post-launch support |
| `completed` | Project finished |
| `on_hold` | Paused |

### Project Data Schema

```json
{
  "id": "proj12345",
  "name": "Project Name",
  "client_id": "cli12345",
  "idea_id": "idea67890",
  "description": "Project description",
  "platforms": ["iOS", "Android"],
  "tech_stack": ["Flutter", "Firebase"],
  "revenue_model": "70_30",
  "contract_value": 50000.00,
  "start_date": "2026-01-15",
  "target_launch": "2026-04-15",
  "actual_launch": "",
  "team": ["pm", "dev_lead", "design_lead", "qa_lead"],
  "status": "development",
  "testers": ["tst123", "tst456"],
  "milestones": [
    {
      "id": "m1",
      "name": "Design Complete",
      "due_date": "2026-02-01",
      "deliverables": ["Wireframes", "UI mockups"],
      "completed": true,
      "completed_date": "2026-01-28"
    }
  ],
  "sprints": [...],
  "financials": {
    "invoiced": 25000.00,
    "paid": 25000.00,
    "revenue_share_earned": 0,
    "expenses": 5000.00
  },
  "notes": [...]
}
```

---

## Finances Management

### CLI Commands

```bash
# List invoices
python orchestrator.py finances invoices
python orchestrator.py finances invoices --status sent
python orchestrator.py finances invoices --status overdue

# Create invoice
python orchestrator.py finances create-invoice \
  --client <client_id> \
  --project <project_id> \
  --amount 10000 \
  --description "Development milestone 1" \
  --due-date 2026-02-15

# Generate financial report
python orchestrator.py finances report
python orchestrator.py finances report --period 2026-01
```

### Invoice Statuses

| Status | Description |
|--------|-------------|
| `draft` | Created but not sent |
| `sent` | Sent to client |
| `paid` | Payment received |
| `overdue` | Past due date |
| `cancelled` | Cancelled |

### Financial Records

The finances store tracks:

1. **Invoices** — Bills sent to clients
2. **Payments** — Money received or paid out
3. **Expenses** — Business expenses
4. **Revenue Shares** — Revenue share earnings from clients

---

## Report Generation

### Generate All Reports

```bash
python orchestrator.py report all
```

### Individual Reports

```bash
# Ideas pipeline
python orchestrator.py ideas report

# Tester program
python orchestrator.py testers report

# Projects status
python orchestrator.py projects report

# Financial summary
python orchestrator.py finances report
python orchestrator.py finances report --period 2026-01

# Client report
python orchestrator.py clients report <client_id>

# Idea detail report
python orchestrator.py ideas report --id <idea_id>
```

Reports are saved to the `reports/` directory as markdown files.

---

## Communication Templates

Templates in `templates/emails/` can be used to communicate with:

### Ideas Submitters
- `idea_received.md` — Acknowledge submission
- `idea_approved.md` — Notify of approval with details
- `idea_declined.md` — Notify of rejection with reasoning

### Testers
- `tester_welcome.md` — Welcome to the program
- `tester_assignment.md` — Project assignment details

### Template Variables

Templates use `{{ variable }}` placeholders:

```markdown
Hi {{ submitter_name }},

Thank you for submitting **{{ idea_name }}**...
```

---

## Agent Integration

Agents can access data through context files. The data store can generate context summaries for agent meetings:

### Ideas Context
- Pending ideas count
- Ideas under review
- Recently approved ideas

### Projects Context
- Active projects with status
- Upcoming milestones
- Resource allocation

### Financial Context
- Outstanding invoices
- Revenue this period
- Cash flow status

---

## Best Practices

### Data Entry
1. Always include contact email for ideas and testers
2. Use consistent naming for platforms (iOS, Android, Web, Desktop)
3. Add notes when changing statuses

### Communication
1. Log all communications (calls, emails, meetings)
2. Use templates for consistent messaging
3. Track follow-ups needed

### Reports
1. Generate reports weekly for standups
2. Generate financial reports monthly
3. Generate client reports before key meetings

### Data Hygiene
1. Update project status as it progresses
2. Mark invoices as paid when received
3. Archive completed projects periodically
