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

# Agent configuration
DEFAULT_AGENTS = ["cito", "pm", "dev_lead", "qa_lead", "customer_success", "marketing"]
DEFAULT_FACILITATOR = "cito"

# Meeting type configurations
MEETING_TYPES = {
    "standup": {
        "name": "Daily Standup",
        "default_agents": DEFAULT_AGENTS,
        "facilitator": "pm",
        "include_context": ["company"],
    },
    "strategy": {
        "name": "Strategy Session",
        "default_agents": ["cito", "pm", "dev_lead"],
        "facilitator": "cito",
        "include_context": ["company", "active_projects"],
    },
    "idea_review": {
        "name": "Idea Review",
        "default_agents": DEFAULT_AGENTS,
        "facilitator": "cito",
        "include_context": ["company", "active_projects", "pending_ideas"],
    },
    "retro": {
        "name": "Retrospective",
        "default_agents": DEFAULT_AGENTS,
        "facilitator": "pm",
        "include_context": ["company", "active_projects"],
    },
    "custom": {
        "name": "Custom Meeting",
        "default_agents": ["cito", "pm", "dev_lead"],
        "facilitator": "cito",
        "include_context": ["company"],
    },
}

# Display names for agents
AGENT_DISPLAY_NAMES = {
    "cito": "CITO",
    "pm": "PM",
    "dev_lead": "DevLead",
    "qa_lead": "QALead",
    "customer_success": "CustomerSuccess",
    "marketing": "Marketing",
}
