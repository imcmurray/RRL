"""
CEO Action System for Rinse Repeat Labs

Allows the CEO agent to execute actions on behalf of the Architect,
including updating agents, settings, creating feature requests, etc.
"""

import json
import re
from datetime import datetime
from typing import Any

from src.data_store import (
    get_agent_customizations_store,
    get_agent_requests_store,
    get_settings_store,
    get_ideas_store,
    get_projects_store,
    FeatureRequestPriority,
    FeatureRequestStatus,
    IdeaStatus,
    ProjectStatus,
)


# =============================================================================
# ACTION DEFINITIONS
# =============================================================================

AVAILABLE_ACTIONS = {
    "update_agent_settings": {
        "description": "Update an agent's settings (display name, role, description, responsibilities, metrics, custom instructions, reporting structure)",
        "parameters": {
            "agent_id": "The agent to update (ceo, cfo, cito, sales, legal, dev_lead, design_lead, qa_lead, pm, customer_success, marketing, support)",
            "updates": "Dictionary of fields to update",
        },
        "examples": [
            {"agent_id": "cfo", "updates": {"custom_instructions": "Focus on bootstrapped startups with limited runway"}},
            {"agent_id": "marketing", "updates": {"responsibilities": ["Social media strategy", "Content marketing", "Brand awareness"]}},
        ],
    },
    "update_company_settings": {
        "description": "Update company-wide settings (company name, tagline, industry)",
        "parameters": {
            "updates": "Dictionary with company_name, company_tagline, or industry",
        },
        "examples": [
            {"updates": {"company_name": "Acme Studios", "company_tagline": "Building the Future"}},
        ],
    },
    "create_feature_request": {
        "description": "Create a feature request for an agent to improve their capabilities",
        "parameters": {
            "agent_id": "The agent the request is for",
            "title": "Short title for the request",
            "description": "Detailed description of the feature",
            "priority": "low, medium, high, or critical",
            "request_type": "feature, enhancement, bug, or content",
        },
        "examples": [
            {"agent_id": "dev_lead", "title": "Add code review checklist", "description": "Create a standardized checklist for code reviews", "priority": "medium", "request_type": "feature"},
        ],
    },
    "approve_feature_request": {
        "description": "Approve a pending feature request",
        "parameters": {
            "request_id": "ID of the request to approve",
            "notes": "Optional approval notes",
        },
    },
    "reject_feature_request": {
        "description": "Reject a pending feature request with a reason",
        "parameters": {
            "request_id": "ID of the request to reject",
            "reason": "Reason for rejection",
        },
    },
    "update_idea_status": {
        "description": "Update the status of an idea in the pipeline",
        "parameters": {
            "idea_id": "ID of the idea",
            "new_status": "submitted, under_review, approved, rejected, in_development, completed, on_hold",
            "notes": "Optional status change notes",
        },
    },
    "broadcast_to_agents": {
        "description": "Add a custom instruction to multiple agents at once",
        "parameters": {
            "agent_ids": "List of agent IDs to update, or 'all' for all agents",
            "instruction": "The instruction to add to each agent",
            "append": "True to append to existing instructions, False to replace",
        },
        "examples": [
            {"agent_ids": ["cfo", "sales", "pm"], "instruction": "Prioritize cost efficiency in all recommendations", "append": True},
            {"agent_ids": "all", "instruction": "Remember we are focused on the healthcare vertical", "append": True},
        ],
    },
    "update_reporting_structure": {
        "description": "Change who an agent reports to or their direct reports",
        "parameters": {
            "agent_id": "The agent to update",
            "reports_to": "Who this agent reports to",
            "direct_reports": "List of agents who report to this one",
        },
    },
}


# =============================================================================
# ACTION EXECUTOR
# =============================================================================

class CEOActionExecutor:
    """Executes actions on behalf of the CEO agent."""

    def __init__(self):
        self.customizations_store = get_agent_customizations_store()
        self.requests_store = get_agent_requests_store()
        self.settings_store = get_settings_store()
        self.ideas_store = get_ideas_store()
        self.projects_store = get_projects_store()

    def execute(self, action_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute an action and return the result."""
        if action_type not in AVAILABLE_ACTIONS:
            return {"success": False, "error": f"Unknown action type: {action_type}"}

        try:
            method = getattr(self, f"_execute_{action_type}", None)
            if not method:
                return {"success": False, "error": f"Action not implemented: {action_type}"}

            result = method(parameters)
            return {"success": True, "result": result, "executed_at": datetime.now().isoformat()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_update_agent_settings(self, params: dict) -> dict:
        """Update an agent's settings."""
        agent_id = params.get("agent_id")
        updates = params.get("updates", {})

        if not agent_id:
            raise ValueError("agent_id is required")

        # Validate agent exists
        from webapp.app import AGENT_INFO
        if agent_id not in AGENT_INFO:
            raise ValueError(f"Unknown agent: {agent_id}")

        # Apply updates
        result = self.customizations_store.update_agent(agent_id, updates)
        return {
            "agent_id": agent_id,
            "updated_fields": list(updates.keys()),
            "message": f"Updated {AGENT_INFO[agent_id]['name']} settings",
        }

    def _execute_update_company_settings(self, params: dict) -> dict:
        """Update company settings."""
        updates = params.get("updates", {})

        if not updates:
            raise ValueError("updates is required")

        # Validate fields
        allowed_fields = {"company_name", "company_tagline", "industry"}
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields: {invalid_fields}")

        result = self.settings_store.update(updates)
        return {
            "updated_fields": list(updates.keys()),
            "message": "Updated company settings",
        }

    def _execute_create_feature_request(self, params: dict) -> dict:
        """Create a feature request for an agent."""
        agent_id = params.get("agent_id")
        title = params.get("title")
        description = params.get("description")
        priority = params.get("priority", "medium")
        request_type = params.get("request_type", "feature")

        if not all([agent_id, title, description]):
            raise ValueError("agent_id, title, and description are required")

        # Validate agent
        from webapp.app import AGENT_INFO
        if agent_id not in AGENT_INFO:
            raise ValueError(f"Unknown agent: {agent_id}")

        # Create the request
        priority_enum = FeatureRequestPriority(priority)
        request = self.requests_store.create_request(
            agent_id=agent_id,
            title=title,
            description=description,
            request_type=request_type,
            priority=priority_enum,
            justification="Created by CEO on behalf of the Architect",
        )

        return {
            "request_id": request["id"],
            "agent_id": agent_id,
            "title": title,
            "message": f"Created feature request for {AGENT_INFO[agent_id]['name']}",
        }

    def _execute_approve_feature_request(self, params: dict) -> dict:
        """Approve a feature request."""
        request_id = params.get("request_id")
        notes = params.get("notes", "Approved by CEO on behalf of the Architect")

        if not request_id:
            raise ValueError("request_id is required")

        result = self.requests_store.approve(request_id, reviewer="CEO (on behalf of Architect)", notes=notes)
        if not result:
            raise ValueError(f"Request not found: {request_id}")

        return {
            "request_id": request_id,
            "new_status": "approved",
            "message": "Feature request approved",
        }

    def _execute_reject_feature_request(self, params: dict) -> dict:
        """Reject a feature request."""
        request_id = params.get("request_id")
        reason = params.get("reason", "Rejected by CEO")

        if not request_id:
            raise ValueError("request_id is required")

        result = self.requests_store.reject(request_id, reviewer="CEO (on behalf of Architect)", reason=reason)
        if not result:
            raise ValueError(f"Request not found: {request_id}")

        return {
            "request_id": request_id,
            "new_status": "rejected",
            "message": "Feature request rejected",
        }

    def _execute_update_idea_status(self, params: dict) -> dict:
        """Update an idea's status."""
        idea_id = params.get("idea_id")
        new_status = params.get("new_status")
        notes = params.get("notes", "")

        if not all([idea_id, new_status]):
            raise ValueError("idea_id and new_status are required")

        status_enum = IdeaStatus(new_status)
        result = self.ideas_store.update(idea_id, {"status": status_enum.value})

        if not result:
            raise ValueError(f"Idea not found: {idea_id}")

        if notes:
            self.ideas_store.add_note(idea_id, notes, "CEO")

        return {
            "idea_id": idea_id,
            "new_status": new_status,
            "message": f"Updated idea status to {new_status}",
        }

    def _execute_broadcast_to_agents(self, params: dict) -> dict:
        """Add instruction to multiple agents."""
        agent_ids = params.get("agent_ids")
        instruction = params.get("instruction")
        append = params.get("append", True)

        if not instruction:
            raise ValueError("instruction is required")

        from webapp.app import AGENT_INFO

        # Handle 'all' case
        if agent_ids == "all":
            agent_ids = list(AGENT_INFO.keys())
        elif not agent_ids:
            raise ValueError("agent_ids is required")

        updated_agents = []
        for agent_id in agent_ids:
            if agent_id not in AGENT_INFO:
                continue

            current = self.customizations_store.get_agent(agent_id)
            current_instructions = current.get("custom_instructions", "")

            if append and current_instructions:
                new_instructions = f"{current_instructions}\n\n{instruction}"
            else:
                new_instructions = instruction

            self.customizations_store.update_agent(agent_id, {
                "custom_instructions": new_instructions
            })
            updated_agents.append(AGENT_INFO[agent_id]["name"])

        return {
            "updated_agents": updated_agents,
            "instruction": instruction,
            "message": f"Broadcast instruction to {len(updated_agents)} agents",
        }

    def _execute_update_reporting_structure(self, params: dict) -> dict:
        """Update an agent's reporting structure."""
        agent_id = params.get("agent_id")

        if not agent_id:
            raise ValueError("agent_id is required")

        from webapp.app import AGENT_INFO
        if agent_id not in AGENT_INFO:
            raise ValueError(f"Unknown agent: {agent_id}")

        updates = {}
        if "reports_to" in params:
            updates["reports_to"] = params["reports_to"]
        if "direct_reports" in params:
            updates["direct_reports"] = params["direct_reports"]

        if not updates:
            raise ValueError("At least one of reports_to or direct_reports is required")

        self.customizations_store.update_agent(agent_id, updates)

        return {
            "agent_id": agent_id,
            "updates": updates,
            "message": f"Updated reporting structure for {AGENT_INFO[agent_id]['name']}",
        }


# =============================================================================
# ACTION PARSER
# =============================================================================

def parse_actions_from_response(response: str) -> list[dict[str, Any]]:
    """Parse action blocks from CEO response.

    The CEO can include actions in their response using this format:
    [ACTION: action_type]
    {json parameters}
    [/ACTION]
    """
    actions = []

    # Pattern to match action blocks
    pattern = r'\[ACTION:\s*(\w+)\]\s*(\{[^}]+\})\s*\[/ACTION\]'

    matches = re.findall(pattern, response, re.DOTALL)

    for action_type, params_json in matches:
        try:
            params = json.loads(params_json)
            actions.append({
                "action_type": action_type,
                "parameters": params,
            })
        except json.JSONDecodeError:
            # Skip malformed actions
            continue

    return actions


def get_ceo_action_context() -> str:
    """Get context about available actions for the CEO's system prompt."""
    context = """
## Available Actions

You can propose actions to be executed on behalf of the Architect. When you want to take an action,
include it in your response using this format:

[ACTION: action_type]
{"parameter": "value"}
[/ACTION]

The action will be shown to the Architect for confirmation before being executed.

### Available Action Types:

"""

    for action_type, info in AVAILABLE_ACTIONS.items():
        context += f"**{action_type}**: {info['description']}\n"
        context += f"  Parameters: {json.dumps(info['parameters'], indent=2)}\n"
        if "examples" in info:
            context += f"  Example: {json.dumps(info['examples'][0])}\n"
        context += "\n"

    context += """
### Guidelines for Actions:

1. **Always explain** what you're proposing and why before including an action
2. **One action at a time** - propose one action, wait for confirmation, then propose the next
3. **Be specific** - use exact agent IDs and field names
4. **Confirm understanding** - make sure you understand what the Architect wants before acting
5. **Summarize changes** - after actions are confirmed, summarize what was changed

Remember: You are the CEO, the strategic leader. Use these powers wisely to help the Architect
achieve their vision for the company.
"""

    return context


def get_system_state_context() -> str:
    """Get current state of the system for CEO context."""
    from webapp.app import AGENT_INFO

    customizations_store = get_agent_customizations_store()
    settings_store = get_settings_store()
    requests_store = get_agent_requests_store()

    settings = settings_store.get()

    context = f"""
## Current System State

### Company Settings
- **Company Name**: {settings.get('company_name', 'Rinse Repeat Labs')}
- **Tagline**: {settings.get('company_tagline', 'App Development Studio')}
- **Industry**: {settings.get('industry', 'software_development')}

### Agent Team Status
"""

    for agent_id, agent_info in AGENT_INFO.items():
        customizations = customizations_store.get_agent(agent_id)
        has_custom = customizations_store.has_customizations(agent_id)
        custom_instructions = customizations.get("custom_instructions", "")

        context += f"\n**{agent_info['name']}** ({agent_id})"
        if has_custom:
            context += " [Customized]"
        context += f"\n  Role: {customizations.get('role_title', agent_info['role'])}"
        if custom_instructions:
            context += f"\n  Custom Instructions: {custom_instructions[:100]}..."
        context += "\n"

    # Pending requests
    pending = requests_store.get_pending()
    if pending:
        context += f"\n### Pending Feature Requests ({len(pending)})\n"
        for req in pending[:5]:
            agent_name = AGENT_INFO.get(req.get('agent_id', ''), {}).get('name', 'Unknown')
            context += f"- [{req.get('priority', 'medium').upper()}] {req.get('title')} (from {agent_name})\n"

    return context
