"""Utility functions for the Rinse Repeat Labs Agent Orchestrator."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import config


def format_timestamp(dt: datetime | None = None) -> str:
    """Format a datetime for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")


def format_date(dt: datetime | None = None) -> str:
    """Format a datetime as a date string."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def load_file(path: Path) -> str:
    """Load content from a file."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def save_file(path: Path, content: str) -> None:
    """Save content to a file, creating directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_context(context_types: list[str] | None = None) -> str:
    """Load and combine context files.

    Args:
        context_types: List of context types to load. Options: "company", "active_projects", "pending_ideas"
                      If None, loads only company context.

    Returns:
        Combined context as a string.
    """
    if context_types is None:
        context_types = ["company"]

    context_parts = []

    context_files = {
        "company": config.COMPANY_CONTEXT_FILE,
        "active_projects": config.ACTIVE_PROJECTS_FILE,
        "pending_ideas": config.PENDING_IDEAS_FILE,
    }

    for context_type in context_types:
        if context_type in context_files:
            content = load_file(context_files[context_type])
            if content:
                context_parts.append(content)

    return "\n\n---\n\n".join(context_parts)


def load_meeting_transcript(meeting_file: str | Path) -> str:
    """Load a meeting transcript."""
    path = Path(meeting_file)
    if not path.is_absolute():
        path = config.MEETINGS_DIR / path
    return load_file(path)


def save_meeting_transcript(
    meeting_type: str,
    topic: str,
    content: str,
    dt: datetime | None = None,
) -> Path:
    """Save a meeting transcript to a file.

    Args:
        meeting_type: Type of meeting (standup, strategy, etc.)
        topic: Meeting topic
        content: Full transcript content
        dt: Datetime of meeting (defaults to now)

    Returns:
        Path to the saved file.
    """
    if dt is None:
        dt = datetime.now()

    date_str = format_date(dt)
    topic_slug = slugify(topic)
    filename = f"{date_str}-{meeting_type}-{topic_slug}.md"

    path = config.MEETINGS_DIR / filename
    save_file(path, content)
    return path


def list_meetings(limit: int | None = None) -> list[dict[str, Any]]:
    """List meeting transcripts.

    Args:
        limit: Maximum number of meetings to return (most recent first)

    Returns:
        List of meeting info dictionaries.
    """
    meetings = []

    if config.MEETINGS_DIR.exists():
        for path in sorted(config.MEETINGS_DIR.glob("*.md"), reverse=True):
            # Parse filename: YYYY-MM-DD-type-topic.md
            parts = path.stem.split("-", 4)
            if len(parts) >= 4:
                date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                meeting_type = parts[3] if len(parts) > 3 else "unknown"
                topic = parts[4].replace("-", " ") if len(parts) > 4 else "untitled"

                meetings.append({
                    "path": path,
                    "date": date_str,
                    "type": meeting_type,
                    "topic": topic,
                    "filename": path.name,
                })

            if limit and len(meetings) >= limit:
                break

    return meetings


def load_decisions() -> list[dict[str, Any]]:
    """Load all decisions from the decisions file."""
    if config.DECISIONS_FILE.exists():
        content = config.DECISIONS_FILE.read_text(encoding="utf-8")
        if content.strip():
            return json.loads(content)
    return []


def save_decision(decision: dict[str, Any]) -> None:
    """Append a decision to the decisions file.

    Args:
        decision: Decision dictionary with keys:
            - date: ISO date string
            - topic: Topic of the decision
            - decision: The decision made
            - rationale: Why this decision was made
            - owner: Who is responsible
            - status: Current status (pending, in_progress, completed)
            - meeting: Optional reference to meeting file
    """
    decisions = load_decisions()

    # Add ID if not present
    if "id" not in decision:
        decision["id"] = len(decisions) + 1

    # Add timestamp if not present
    if "date" not in decision:
        decision["date"] = format_date()

    decisions.append(decision)

    config.DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.DECISIONS_FILE.write_text(
        json.dumps(decisions, indent=2),
        encoding="utf-8"
    )


def query_decisions(
    topic: str | None = None,
    status: str | None = None,
    owner: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Query decisions with optional filters.

    Args:
        topic: Filter by topic (substring match)
        status: Filter by status
        owner: Filter by owner
        limit: Maximum number of results

    Returns:
        Filtered list of decisions.
    """
    decisions = load_decisions()

    # Apply filters
    if topic:
        topic_lower = topic.lower()
        decisions = [d for d in decisions if topic_lower in d.get("topic", "").lower()]

    if status:
        decisions = [d for d in decisions if d.get("status") == status]

    if owner:
        owner_lower = owner.lower()
        decisions = [d for d in decisions if owner_lower in d.get("owner", "").lower()]

    # Sort by date (most recent first)
    decisions = sorted(decisions, key=lambda d: d.get("date", ""), reverse=True)

    # Apply limit
    if limit:
        decisions = decisions[:limit]

    return decisions


def parse_agent_markdown(content: str) -> dict[str, str]:
    """Parse an agent markdown file into its components.

    Args:
        content: Raw markdown content

    Returns:
        Dictionary with keys: name, role, expertise, responsibilities,
        communication_style, system_prompt
    """
    result = {
        "name": "",
        "role": "",
        "expertise": "",
        "responsibilities": "",
        "communication_style": "",
        "system_prompt": "",
    }

    # Extract name from first heading
    name_match = re.search(r"^#\s+Agent:\s*(.+)$", content, re.MULTILINE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    # Extract sections
    sections = {
        "role": r"##\s+Role\s*\n(.*?)(?=\n##|\Z)",
        "expertise": r"##\s+Expertise\s*\n(.*?)(?=\n##|\Z)",
        "responsibilities": r"##\s+Responsibilities\s*\n(.*?)(?=\n##|\Z)",
        "communication_style": r"##\s+Communication Style\s*\n(.*?)(?=\n##|\Z)",
        "system_prompt": r"##\s+System Prompt\s*\n(.*?)(?=\n##|\Z)",
    }

    for key, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            result[key] = match.group(1).strip()

    return result
