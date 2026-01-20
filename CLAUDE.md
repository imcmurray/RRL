# Claude Code Context for Rinse Repeat Labs

## Project Overview

Rinse Repeat Labs (RRL) is an AI-powered app development studio with a 12-agent orchestrator system. The project includes:

- **CLI Orchestrator** (`orchestrator.py`) - Command-line interface for agent meetings and data management
- **Web Dashboard** (`webapp/`) - Flask-based visual management interface
- **Data Stores** (`src/data_store.py`) - JSON-backed persistence layer
- **Agent System** (`agents/`) - 12 specialized AI agents with defined roles

## Quick Start

```bash
# CLI - Run 1:1 meeting with an agent
python orchestrator.py meeting ceo

# CLI - Data management
python orchestrator.py ideas list
python orchestrator.py testers add --name "John" --email "john@test.com"
python orchestrator.py requests pending

# Web Dashboard
cd webapp && python app.py
# Opens at http://localhost:5000
```

## Architecture

```
orchestrator.py          # Main CLI entry point
├── src/
│   ├── data_store.py    # All data stores (Ideas, Testers, Clients, Projects, Finances, AgentRequests)
│   ├── data_cli.py      # Click commands for data management
│   ├── reports.py       # Report generation
│   └── utils.py         # Helper functions
├── agents/              # Agent system prompts (12 markdown files)
├── webapp/
│   ├── app.py           # Flask application with all routes
│   ├── templates/       # Jinja2 templates (Bootstrap 5)
│   └── static/          # CSS, JS assets
└── data/                # JSON data files (gitignored)
```

## The 12 Agents

| ID | Role | Team |
|----|------|------|
| `ceo` | Chief Executive Officer | Executive |
| `cfo` | Chief Financial Officer | Executive |
| `cito` | Chief Information Technology Officer | Executive |
| `sales` | Sales Director | Executive |
| `legal` | Legal Counsel | Executive |
| `dev_lead` | Development Lead | Technical |
| `design_lead` | Design Lead | Technical |
| `qa_lead` | Quality Assurance Lead | Technical |
| `pm` | Project Manager | Operations |
| `customer_success` | Customer Success Manager | Operations |
| `marketing` | Marketing Director | Operations |
| `support` | Support Lead | Operations |

## Data Store Pattern

All stores use singleton pattern and share JSON files between CLI and Web:

```python
from src.data_store import get_ideas_store, get_agent_requests_store

# Get store instance
store = get_ideas_store()

# Common operations
store.get_all()
store.get_by_id(id)
store.create_*(...)
store.update(id, {field: value})
store.delete(id)
```

## Key Files to Know

- `agents/*.md` - Each agent's system prompt and capabilities
- `webapp/app.py` - All web routes including HTMX endpoints (1800+ lines)
- `src/data_store.py` - Data models and persistence
- `config.py` - Configuration and agent list
- `docs/AGENT_PORTALS.md` - Agent portal feature documentation

## Web Dashboard Features

- **HTMX Integration** - Real-time partial page updates without full reloads
- **Agent Portals** - Each agent has a dedicated workspace at `/agents/<agent_id>`
- **Feature Requests** - Agents can submit requests, Architect approves/rejects
- **Shared State** - CLI and Web use same `data/*.json` files

## Common Tasks

### Adding a new data entity
1. Add store class in `src/data_store.py`
2. Add CLI commands in `src/data_cli.py`
3. Register command in `orchestrator.py`
4. Add web routes in `webapp/app.py`
5. Create templates in `webapp/templates/`

### Adding HTMX endpoint
1. Add route in `webapp/app.py` under HTMX section (prefix: `/htmx/`)
2. Create partial template in `webapp/templates/*/partials/`
3. Add `hx-get`, `hx-trigger`, `hx-swap` attributes to target element

### Modifying an agent
1. Edit `agents/<agent_id>.md` for system prompt changes
2. Update `AGENT_INFO` dict in `webapp/app.py` for web portal info

## Testing

```bash
# Check data stores work
python -c "from src.data_store import get_ideas_store; print(get_ideas_store().get_all())"

# Run Flask in debug mode
cd webapp && python app.py

# CLI help
python orchestrator.py --help
python orchestrator.py ideas --help
```

## Conventions

- Bootstrap 5 for all UI components
- Jinja2 templates extend `base.html`
- Agent IDs are lowercase with underscores (e.g., `dev_lead`)
- Status enums defined in `data_store.py`
- All timestamps in ISO 8601 format
