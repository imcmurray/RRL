"""Configuration settings for the Rinse Repeat Labs Agent Orchestrator."""

import os
from pathlib import Path

# Base directory (project root)
BASE_DIR = Path(__file__).parent

# API Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2048

# Directory paths
AGENTS_DIR = BASE_DIR / "agents"
MEETINGS_DIR = BASE_DIR / "meetings"
DECISIONS_DIR = BASE_DIR / "decisions"
CONTEXT_DIR = BASE_DIR / "context"

# File paths
DECISIONS_FILE = DECISIONS_DIR / "decisions.json"
COMPANY_CONTEXT_FILE = CONTEXT_DIR / "company.md"
ACTIVE_PROJECTS_FILE = CONTEXT_DIR / "active_projects.md"
PENDING_IDEAS_FILE = CONTEXT_DIR / "pending_ideas.md"
ARCHITECT_NOTES_FILE = CONTEXT_DIR / "architect_notes.md"

# Complete agent roster (12 agents)
ALL_AGENTS = [
    "ceo", "cfo", "cito", "sales", "legal",  # Executive team
    "dev_lead", "design_lead", "qa_lead",     # Product & Engineering
    "pm", "customer_success", "marketing", "support"  # Operations
]

# Agent groupings by team
EXECUTIVE_TEAM = ["ceo", "cfo", "cito", "sales", "legal"]
TECHNICAL_TEAM = ["cito", "dev_lead", "design_lead", "qa_lead"]
OPERATIONS_TEAM = ["pm", "customer_success", "marketing", "support"]

# Idea review participants (CITO, CFO, Sales, Legal, PM, DesignLead)
IDEA_REVIEW_TEAM = ["cito", "cfo", "sales", "legal", "pm", "design_lead"]

# Default facilitators by meeting type
DEFAULT_FACILITATOR = "ceo"

# Display names for agents
AGENT_DISPLAY_NAMES = {
    "ceo": "CEO",
    "cfo": "CFO",
    "cito": "CITO",
    "sales": "Sales",
    "legal": "Legal",
    "dev_lead": "DevLead",
    "design_lead": "DesignLead",
    "qa_lead": "QALead",
    "pm": "PM",
    "customer_success": "CustomerSuccess",
    "marketing": "Marketing",
    "support": "Support",
}

# Agent reporting structure
AGENT_REPORTS_TO = {
    "ceo": "architect",  # Reports to human principal
    "cfo": "ceo",
    "cito": "ceo",
    "sales": "ceo",
    "legal": "ceo",
    "dev_lead": "cito",
    "design_lead": "cito",
    "qa_lead": "cito",
    "pm": "ceo",
    "customer_success": "pm",
    "marketing": "ceo",
    "support": "pm",
}

# Meeting type configurations
MEETING_TYPES = {
    # 1:1 Meetings (Architect + one agent)
    "1on1": {
        "name": "1:1 Meeting",
        "default_agents": ["ceo"],  # Will be overridden by selected agent
        "facilitator": "ceo",
        "include_context": ["company", "active_projects"],
        "description": "Deep dive with a specific agent on their domain",
    },

    # CEO Sync (special strategic 1:1)
    "ceo_sync": {
        "name": "CEO Sync",
        "default_agents": ["ceo"],
        "facilitator": "ceo",
        "include_context": ["company", "active_projects", "pending_ideas"],
        "description": "Strategic planning and vision alignment with CEO",
    },

    # Executive Meeting (CEO, CFO, CITO, Sales, Legal)
    "exec_meeting": {
        "name": "Executive Meeting",
        "default_agents": EXECUTIVE_TEAM,
        "facilitator": "ceo",
        "include_context": ["company", "active_projects"],
        "description": "C-suite alignment on major business decisions",
    },

    # Technical Meeting (CITO, DevLead, DesignLead, QALead)
    "tech_meeting": {
        "name": "Technical Meeting",
        "default_agents": TECHNICAL_TEAM,
        "facilitator": "cito",
        "include_context": ["company", "active_projects"],
        "description": "Technical deep-dives, architecture decisions, quality standards",
    },

    # Project Meeting (PM + project team)
    "project_meeting": {
        "name": "Project Meeting",
        "default_agents": ["pm", "dev_lead", "design_lead", "qa_lead"],
        "facilitator": "pm",
        "include_context": ["company", "active_projects"],
        "description": "Project-specific coordination and sprint planning",
    },

    # All-Hands Meeting (all 12 agents)
    "all_hands": {
        "name": "All-Hands Meeting",
        "default_agents": ALL_AGENTS,
        "facilitator": "ceo",
        "include_context": ["company", "active_projects"],
        "description": "Full team alignment, major announcements, cross-functional issues",
    },

    # Daily Standup (all operational agents)
    "standup": {
        "name": "Daily Standup",
        "default_agents": ALL_AGENTS,
        "facilitator": "pm",
        "include_context": ["company", "active_projects"],
        "description": "Quick daily sync - done, doing, blocked",
    },

    # Idea Review (CITO, CFO, Sales, Legal, PM, DesignLead)
    "idea_review": {
        "name": "Idea Review",
        "default_agents": IDEA_REVIEW_TEAM,
        "facilitator": "cito",
        "include_context": ["company", "active_projects", "pending_ideas"],
        "description": "Evaluate new client idea submissions from all angles",
    },

    # Retrospective (project team + relevant agents)
    "retro": {
        "name": "Retrospective",
        "default_agents": ["pm", "dev_lead", "design_lead", "qa_lead", "cito"],
        "facilitator": "pm",
        "include_context": ["company", "active_projects"],
        "description": "Learn from completed projects - what went well, what didn't",
    },

    # Strategy Session (custom topic)
    "strategy": {
        "name": "Strategy Session",
        "default_agents": EXECUTIVE_TEAM,
        "facilitator": "ceo",
        "include_context": ["company", "active_projects"],
        "description": "Deep discussion on a strategic topic",
    },

    # Custom Meeting
    "custom": {
        "name": "Custom Meeting",
        "default_agents": ["ceo", "cito", "pm"],
        "facilitator": "ceo",
        "include_context": ["company"],
        "description": "Free-form discussion on any topic",
    },
}

# Decision types and their approvers
DECISION_APPROVERS = {
    "technical_architecture": "cito",
    "technology_stack": "cito",  # CEO approval if major shift
    "project_pricing": "ceo",   # CFO + Sales recommend
    "contract_terms": "ceo",    # Legal + Sales negotiate
    "project_timeline": "ceo",  # PM + CITO recommend
    "hire_contractor": "architect",  # CEO recommends
    "new_partnership": "architect",  # CEO + Sales recommend
    "major_pivot": "architect",      # CEO recommends
    "client_acceptance": "ceo",      # Sales recommends
    "launch_readiness": "cito",      # QALead + PM recommend
}

# Success metrics by agent
AGENT_METRICS = {
    "ceo": ["revenue", "client_count", "team_health"],
    "cfo": ["profit_margin", "cash_flow", "ar_ap"],
    "cito": ["tech_debt", "system_uptime", "idea_conversion"],
    "sales": ["pipeline_value", "conversion_rate", "deal_velocity"],
    "legal": ["contract_turnaround", "compliance_status"],
    "dev_lead": ["code_quality", "velocity", "bug_rate"],
    "design_lead": ["design_consistency", "user_satisfaction"],
    "qa_lead": ["bug_escape_rate", "test_coverage", "release_quality"],
    "pm": ["on_time_delivery", "scope_creep", "client_satisfaction"],
    "customer_success": ["nps", "retention", "expansion_revenue"],
    "marketing": ["app_rankings", "traffic", "conversion"],
    "support": ["response_time", "resolution_rate", "satisfaction"],
}
