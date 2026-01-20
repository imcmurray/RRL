#!/usr/bin/env python3
"""
Rinse Repeat Labs Agent Orchestrator

A command-line tool for coordinating AI agents in virtual meetings.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown

import config
from src.agent import AgentRegistry
from src.meeting import Meeting
from src.utils import (
    query_decisions,
    list_meetings,
    load_file,
    format_date,
)
from src.data_cli import ideas, testers, clients, projects, finances, report, requests

console = Console()


def parse_agents(agents_str: str | None) -> list[str] | None:
    """Parse comma-separated agent string into list."""
    if not agents_str:
        return None
    return [a.strip().lower().replace("-", "_") for a in agents_str.split(",")]


def validate_agents(agent_ids: list[str]) -> list[str]:
    """Validate that all agent IDs exist."""
    registry = AgentRegistry()
    available = registry.list_available()

    invalid = [a for a in agent_ids if a not in available]
    if invalid:
        console.print(f"[red]Unknown agents: {', '.join(invalid)}[/red]")
        console.print(f"[dim]Available agents: {', '.join(available)}[/dim]")
        sys.exit(1)

    return agent_ids


def show_progress(message: str) -> None:
    """Show progress message."""
    console.print(f"[dim]{message}[/dim]")


@click.group()
@click.version_option(version="2.0.0")
def cli():
    """Rinse Repeat Labs Agent Orchestrator

    Coordinate AI agents in virtual meetings for planning, strategy, and decision-making.

    You are the Architect - the human principal who oversees the entire operation.
    """
    pass


# =============================================================================
# 1:1 MEETINGS
# =============================================================================

@cli.command("1on1")
@click.option(
    "--agent",
    "-a",
    required=True,
    help="Agent to meet with (e.g., ceo, cito, pm)",
)
@click.option(
    "--topic",
    "-t",
    help="Topic for the discussion (optional)",
)
def one_on_one(agent: str, topic: str | None):
    """Have a 1:1 meeting with a specific agent.

    Deep dive on their domain, get updates, give direction.

    Examples:
        python orchestrator.py 1on1 --agent ceo
        python orchestrator.py 1on1 --agent cito --topic "Flutter migration concerns"
    """
    agent_id = agent.lower().replace("-", "_")
    validate_agents([agent_id])

    registry = AgentRegistry()
    agent_obj = registry.get(agent_id)
    display_topic = topic or f"1:1 with {agent_obj.display_name}"

    meeting = Meeting(
        meeting_type="1on1",
        topic=display_topic,
        agent_ids=[agent_id],
        facilitator_id=agent_id,
        console=console,
    )

    meeting.run_one_on_one(topic=topic, progress_callback=show_progress)


@cli.command("ceo-sync")
@click.option(
    "--topic",
    "-t",
    help="Topic for the strategic discussion (optional)",
)
def ceo_sync(topic: str | None):
    """Strategic sync with the CEO.

    Discuss vision, review business health, make high-level decisions.

    Examples:
        python orchestrator.py ceo-sync
        python orchestrator.py ceo-sync --topic "Q2 hiring plan"
    """
    display_topic = topic or "CEO Strategic Sync"

    meeting = Meeting(
        meeting_type="ceo_sync",
        topic=display_topic,
        agent_ids=["ceo"],
        facilitator_id="ceo",
        console=console,
    )

    meeting.run_one_on_one(topic=topic, progress_callback=show_progress)


# =============================================================================
# TEAM MEETINGS
# =============================================================================

@cli.command("exec-meeting")
@click.option(
    "--topic",
    "-t",
    help="Topic for the executive meeting",
)
def exec_meeting(topic: str | None):
    """Run an executive team meeting.

    Participants: CEO, CFO, CITO, Sales, Legal

    Purpose: C-suite alignment on major business decisions.

    Examples:
        python orchestrator.py exec-meeting
        python orchestrator.py exec-meeting --topic "New enterprise client opportunity"
    """
    display_topic = topic or "Executive Team Meeting"

    meeting = Meeting(
        meeting_type="exec_meeting",
        topic=display_topic,
        console=console,
    )

    meeting.run_discussion(progress_callback=show_progress)


@cli.command("tech-meeting")
@click.option(
    "--topic",
    "-t",
    help="Topic for the technical meeting",
)
def tech_meeting(topic: str | None):
    """Run a technical team meeting.

    Participants: CITO, DevLead, DesignLead, QALead

    Purpose: Technical deep-dives, architecture decisions, quality standards.

    Examples:
        python orchestrator.py tech-meeting
        python orchestrator.py tech-meeting --topic "Architecture review for FitPulse v2"
    """
    display_topic = topic or "Technical Team Meeting"

    meeting = Meeting(
        meeting_type="tech_meeting",
        topic=display_topic,
        console=console,
    )

    meeting.run_discussion(progress_callback=show_progress)


@cli.command("project-meeting")
@click.option(
    "--project",
    "-p",
    required=True,
    help="Project name for the meeting",
)
@click.option(
    "--topic",
    "-t",
    help="Specific topic for the meeting",
)
@click.option(
    "--agents",
    "-a",
    help="Additional agents to include (comma-separated)",
)
def project_meeting(project: str, topic: str | None, agents: str | None):
    """Run a project-specific meeting.

    Default participants: PM, DevLead, DesignLead, QALead

    Purpose: Sprint planning, blocker resolution, project coordination.

    Examples:
        python orchestrator.py project-meeting --project "TimeFlow"
        python orchestrator.py project-meeting --project "FitPulse" --topic "Sprint 4 planning"
    """
    display_topic = topic or f"Project Meeting: {project}"

    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    meeting = Meeting(
        meeting_type="project_meeting",
        topic=display_topic,
        agent_ids=agent_ids,
        console=console,
    )

    meeting.run_project_meeting(project=project, progress_callback=show_progress)


@cli.command("all-hands")
@click.option(
    "--topic",
    "-t",
    help="Topic for the all-hands meeting",
)
def all_hands(topic: str | None):
    """Run an all-hands meeting with all 12 agents.

    Purpose: Full team alignment, major announcements, cross-functional issues.

    Examples:
        python orchestrator.py all-hands
        python orchestrator.py all-hands --topic "Q1 retrospective and Q2 planning"
    """
    display_topic = topic or "All-Hands Meeting"

    meeting = Meeting(
        meeting_type="all_hands",
        topic=display_topic,
        console=console,
    )

    meeting.run_discussion(progress_callback=show_progress)


# =============================================================================
# OPERATIONAL MEETINGS
# =============================================================================

@cli.command()
@click.option(
    "--agents",
    "-a",
    help="Comma-separated list of agents (default: all)",
)
def standup(agents: str | None):
    """Run a daily standup meeting.

    Each agent reports: done, doing, blocked.

    Examples:
        python orchestrator.py standup
        python orchestrator.py standup --agents "dev_lead,design_lead,qa_lead"
    """
    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    meeting = Meeting(
        meeting_type="standup",
        topic="Daily Standup",
        agent_ids=agent_ids,
        console=console,
    )

    meeting.run_standup(progress_callback=show_progress)


@cli.command("idea-review")
@click.option(
    "--idea",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="Path to idea file to review",
)
@click.option(
    "--agents",
    "-a",
    help="Override default agents (comma-separated)",
)
def idea_review(idea: str, agents: str | None):
    """Review a new idea or proposal.

    Default participants: CITO, CFO, Sales, Legal, PM, DesignLead

    Each participant evaluates from their perspective:
    - CITO: Technical feasibility, stack recommendation
    - CFO: Pricing, profitability analysis
    - Sales: Client fit, deal potential
    - Legal: Contract considerations, IP, compliance
    - PM: Timeline, resource availability
    - DesignLead: UX complexity, design effort

    Examples:
        python orchestrator.py idea-review --idea ideas/fitness-app.md
    """
    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    # Extract topic from filename or first line
    idea_path = Path(idea)
    idea_content = load_file(idea_path)

    # Try to get title from first heading or filename
    topic = idea_path.stem.replace("-", " ").replace("_", " ").title()
    for line in idea_content.split("\n"):
        if line.startswith("# "):
            topic = line[2:].strip()
            break

    meeting = Meeting(
        meeting_type="idea_review",
        topic=f"Idea Review: {topic}",
        agent_ids=agent_ids,
        console=console,
    )

    meeting.run_idea_review(idea_file=idea_path, progress_callback=show_progress)


@cli.command()
@click.option(
    "--project",
    "-p",
    required=True,
    help="Name of the project to review",
)
@click.option(
    "--agents",
    "-a",
    help="Override default agents (comma-separated)",
)
def retro(project: str, agents: str | None):
    """Run a project retrospective.

    What went well, what didn't, lessons learned.

    Examples:
        python orchestrator.py retro --project "ShopWave"
    """
    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    meeting = Meeting(
        meeting_type="retro",
        topic=f"Retrospective: {project}",
        agent_ids=agent_ids,
        console=console,
    )

    meeting.run_retrospective(project=project, progress_callback=show_progress)


@cli.command()
@click.option(
    "--topic",
    "-t",
    required=True,
    help="Topic for the strategy discussion",
)
@click.option(
    "--agents",
    "-a",
    help="Comma-separated list of agents",
)
@click.option(
    "--facilitator",
    "-f",
    help="Facilitator agent ID (default: ceo)",
)
def strategy(topic: str, agents: str | None, facilitator: str | None):
    """Run a strategy session on a specific topic.

    Examples:
        python orchestrator.py strategy --topic "Should we adopt Flutter?"
        python orchestrator.py strategy --topic "Q3 priorities" --agents ceo,cfo,cito,pm
    """
    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    if facilitator:
        validate_agents([facilitator])

    meeting = Meeting(
        meeting_type="strategy",
        topic=topic,
        agent_ids=agent_ids,
        facilitator_id=facilitator,
        console=console,
    )

    meeting.run_discussion(progress_callback=show_progress)


@cli.command()
@click.option(
    "--topic",
    "-t",
    required=True,
    help="Topic for the meeting",
)
@click.option(
    "--agents",
    "-a",
    help="Comma-separated list of agents",
)
@click.option(
    "--facilitator",
    "-f",
    help="Facilitator agent ID",
)
def meeting(topic: str, agents: str | None, facilitator: str | None):
    """Run a custom meeting on any topic.

    Examples:
        python orchestrator.py meeting --topic "Marketing budget" --agents ceo,cfo,marketing
    """
    agent_ids = parse_agents(agents)
    if agent_ids:
        agent_ids = validate_agents(agent_ids)

    if facilitator:
        validate_agents([facilitator])

    mtg = Meeting(
        meeting_type="custom",
        topic=topic,
        agent_ids=agent_ids,
        facilitator_id=facilitator,
        console=console,
    )

    mtg.run_discussion(progress_callback=show_progress)


# =============================================================================
# UTILITIES
# =============================================================================

@cli.command()
@click.option(
    "--last",
    "-n",
    default=10,
    help="Number of recent decisions to show",
)
@click.option(
    "--topic",
    "-t",
    help="Filter by topic (substring match)",
)
@click.option(
    "--status",
    "-s",
    type=click.Choice(["pending", "in_progress", "completed"]),
    help="Filter by status",
)
@click.option(
    "--owner",
    "-o",
    help="Filter by owner",
)
def decisions(last: int, topic: str | None, status: str | None, owner: str | None):
    """View and filter past decisions.

    Examples:
        python orchestrator.py decisions --last 10
        python orchestrator.py decisions --topic "Flutter"
    """
    results = query_decisions(topic=topic, status=status, owner=owner, limit=last)

    if not results:
        console.print("[yellow]No decisions found matching criteria.[/yellow]")
        return

    table = Table(title="Decisions")
    table.add_column("ID", style="dim")
    table.add_column("Date")
    table.add_column("Topic")
    table.add_column("Decision")
    table.add_column("Owner")
    table.add_column("Status")

    for d in results:
        status_style = {
            "pending": "yellow",
            "in_progress": "blue",
            "completed": "green",
        }.get(d.get("status", ""), "")

        table.add_row(
            str(d.get("id", "")),
            d.get("date", ""),
            d.get("topic", "")[:30],
            d.get("decision", "")[:40],
            d.get("owner", ""),
            f"[{status_style}]{d.get('status', '')}[/{status_style}]",
        )

    console.print(table)


@cli.command("meetings")
@click.option(
    "--last",
    "-n",
    default=10,
    help="Number of recent meetings to show",
)
def list_meetings_cmd(last: int):
    """View past meeting transcripts."""
    meetings = list_meetings(limit=last)

    if not meetings:
        console.print("[yellow]No meetings found.[/yellow]")
        return

    table = Table(title="Recent Meetings")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Topic")
    table.add_column("File")

    for m in meetings:
        table.add_row(
            m["date"],
            m["type"],
            m["topic"][:40],
            m["filename"],
        )

    console.print(table)


@cli.command()
def agents():
    """List all available agents."""
    registry = AgentRegistry()
    available = registry.list_available()

    # Group agents by team
    exec_team = []
    tech_team = []
    ops_team = []

    for agent_id in available:
        if agent_id in config.EXECUTIVE_TEAM:
            exec_team.append(agent_id)
        elif agent_id in config.TECHNICAL_TEAM:
            tech_team.append(agent_id)
        else:
            ops_team.append(agent_id)

    def print_agent_table(title: str, agent_list: list[str]):
        if not agent_list:
            return
        table = Table(title=title)
        table.add_column("ID")
        table.add_column("Display Name")
        table.add_column("Role")
        table.add_column("Reports To")

        for agent_id in agent_list:
            try:
                agent = registry.get(agent_id)
                reports_to = config.AGENT_REPORTS_TO.get(agent_id, "—")
                table.add_row(
                    agent_id,
                    agent.display_name,
                    agent.role[:50] if agent.role else "",
                    reports_to.upper() if reports_to != "architect" else "Architect",
                )
            except Exception as e:
                table.add_row(agent_id, "[error]", str(e)[:40], "")

        console.print(table)
        console.print()

    print_agent_table("Executive Team", exec_team)
    print_agent_table("Technical Team", tech_team)
    print_agent_table("Operations Team", ops_team)


@cli.command()
def status():
    """Show company status dashboard.

    Displays agent roster, recent meetings, and recent decisions.
    """
    console.print()
    console.print(
        Panel(
            "[bold cyan]Rinse Repeat Labs[/bold cyan] — Company Dashboard",
            border_style="cyan",
        )
    )
    console.print()

    # Agent count
    registry = AgentRegistry()
    available = registry.list_available()
    console.print(f"[bold]Agents:[/bold] {len(available)} active")
    console.print(f"  Executive: {len([a for a in available if a in config.EXECUTIVE_TEAM])}")
    console.print(f"  Technical: {len([a for a in available if a in config.TECHNICAL_TEAM])}")
    console.print(f"  Operations: {len([a for a in available if a not in config.EXECUTIVE_TEAM and a not in config.TECHNICAL_TEAM])}")
    console.print()

    # Recent meetings
    recent_meetings = list_meetings(limit=5)
    if recent_meetings:
        console.print("[bold]Recent Meetings:[/bold]")
        for m in recent_meetings:
            console.print(f"  {m['date']} - {m['type']} - {m['topic'][:40]}")
    else:
        console.print("[dim]No recent meetings[/dim]")
    console.print()

    # Recent decisions
    recent_decisions = query_decisions(limit=5)
    if recent_decisions:
        console.print("[bold]Recent Decisions:[/bold]")
        for d in recent_decisions:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(d.get("status", ""), "")
            console.print(f"  {status_icon} {d.get('topic', '')[:30]} - {d.get('decision', '')[:30]}")
    else:
        console.print("[dim]No recent decisions[/dim]")
    console.print()


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

@cli.command()
def interactive():
    """Run in interactive mode with a menu.

    Recommended for exploration and getting started.
    """
    registry = AgentRegistry()
    available_agents = registry.list_available()

    while True:
        console.print()
        console.print(
            Panel(
                "[bold cyan]Rinse Repeat Labs[/bold cyan] — Agent Orchestrator\n"
                "   Welcome, Architect.",
                border_style="cyan",
            )
        )
        console.print()
        console.print("What would you like to do?")
        console.print()

        console.print("  [bold]1:1 Meetings[/bold]")
        console.print("  [dim]─────────────[/dim]")
        console.print("  [bold]1.[/bold]  CEO Sync (strategic planning)")
        console.print("  [bold]2.[/bold]  1:1 with an agent")
        console.print()

        console.print("  [bold]Team Meetings[/bold]")
        console.print("  [dim]─────────────[/dim]")
        console.print("  [bold]3.[/bold]  Executive meeting (CEO, CFO, CITO, Sales, Legal)")
        console.print("  [bold]4.[/bold]  Technical meeting (CITO, DevLead, DesignLead, QALead)")
        console.print("  [bold]5.[/bold]  Project meeting")
        console.print("  [bold]6.[/bold]  All-hands (everyone)")
        console.print()

        console.print("  [bold]Operations[/bold]")
        console.print("  [dim]─────────────[/dim]")
        console.print("  [bold]7.[/bold]  Daily standup")
        console.print("  [bold]8.[/bold]  Review an idea submission")
        console.print("  [bold]9.[/bold]  Project retrospective")
        console.print("  [bold]10.[/bold] Strategy session")
        console.print("  [bold]11.[/bold] Custom meeting")
        console.print()

        console.print("  [bold]Utilities[/bold]")
        console.print("  [dim]─────────────[/dim]")
        console.print("  [bold]12.[/bold] View past meetings")
        console.print("  [bold]13.[/bold] View decisions")
        console.print("  [bold]14.[/bold] Company status dashboard")
        console.print("  [bold]15.[/bold] List all agents")
        console.print()

        console.print("  [bold]0.[/bold] Exit")
        console.print()

        choice = Prompt.ask(
            "Select an option",
            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        )

        try:
            if choice == "0":
                console.print("[cyan]Goodbye, Architect![/cyan]")
                break

            elif choice == "1":
                # CEO Sync
                topic = Prompt.ask("Enter topic (or Enter for general sync)", default="")
                meeting = Meeting(
                    meeting_type="ceo_sync",
                    topic=topic or "CEO Strategic Sync",
                    agent_ids=["ceo"],
                    facilitator_id="ceo",
                    console=console,
                )
                meeting.run_one_on_one(topic=topic or None, progress_callback=show_progress)

            elif choice == "2":
                # 1:1 with agent
                console.print("\nAvailable agents:")
                for i, agent_id in enumerate(available_agents, 1):
                    agent = registry.get(agent_id)
                    console.print(f"  {i}. {agent.display_name} ({agent_id})")

                agent_choice = Prompt.ask("Enter agent ID or number")
                if agent_choice.isdigit():
                    idx = int(agent_choice) - 1
                    if 0 <= idx < len(available_agents):
                        agent_id = available_agents[idx]
                    else:
                        console.print("[red]Invalid selection[/red]")
                        continue
                else:
                    agent_id = agent_choice.lower().replace("-", "_")
                    if agent_id not in available_agents:
                        console.print(f"[red]Unknown agent: {agent_id}[/red]")
                        continue

                topic = Prompt.ask("Enter topic (or Enter for general)", default="")
                agent_obj = registry.get(agent_id)
                meeting = Meeting(
                    meeting_type="1on1",
                    topic=topic or f"1:1 with {agent_obj.display_name}",
                    agent_ids=[agent_id],
                    facilitator_id=agent_id,
                    console=console,
                )
                meeting.run_one_on_one(topic=topic or None, progress_callback=show_progress)

            elif choice == "3":
                # Executive meeting
                topic = Prompt.ask("Enter topic (or Enter for general)", default="")
                meeting = Meeting(
                    meeting_type="exec_meeting",
                    topic=topic or "Executive Team Meeting",
                    console=console,
                )
                meeting.run_discussion(progress_callback=show_progress)

            elif choice == "4":
                # Technical meeting
                topic = Prompt.ask("Enter topic (or Enter for general)", default="")
                meeting = Meeting(
                    meeting_type="tech_meeting",
                    topic=topic or "Technical Team Meeting",
                    console=console,
                )
                meeting.run_discussion(progress_callback=show_progress)

            elif choice == "5":
                # Project meeting
                project = Prompt.ask("Enter project name")
                topic = Prompt.ask("Enter specific topic (or Enter for general)", default="")
                meeting = Meeting(
                    meeting_type="project_meeting",
                    topic=topic or f"Project Meeting: {project}",
                    console=console,
                )
                meeting.run_project_meeting(project=project, progress_callback=show_progress)

            elif choice == "6":
                # All-hands
                topic = Prompt.ask("Enter topic (or Enter for general)", default="")
                meeting = Meeting(
                    meeting_type="all_hands",
                    topic=topic or "All-Hands Meeting",
                    console=console,
                )
                meeting.run_discussion(progress_callback=show_progress)

            elif choice == "7":
                # Standup
                meeting = Meeting(
                    meeting_type="standup",
                    topic="Daily Standup",
                    console=console,
                )
                meeting.run_standup(progress_callback=show_progress)

            elif choice == "8":
                # Idea review
                idea_path = Prompt.ask("Enter path to idea file")
                if not Path(idea_path).exists():
                    console.print(f"[red]File not found: {idea_path}[/red]")
                    continue

                idea_content = load_file(Path(idea_path))
                topic = Path(idea_path).stem.replace("-", " ").replace("_", " ").title()
                for line in idea_content.split("\n"):
                    if line.startswith("# "):
                        topic = line[2:].strip()
                        break

                meeting = Meeting(
                    meeting_type="idea_review",
                    topic=f"Idea Review: {topic}",
                    console=console,
                )
                meeting.run_idea_review(idea_file=idea_path, progress_callback=show_progress)

            elif choice == "9":
                # Retrospective
                project = Prompt.ask("Enter project name")
                meeting = Meeting(
                    meeting_type="retro",
                    topic=f"Retrospective: {project}",
                    console=console,
                )
                meeting.run_retrospective(project=project, progress_callback=show_progress)

            elif choice == "10":
                # Strategy session
                topic = Prompt.ask("Enter the strategy topic")
                agents_input = Prompt.ask(
                    "Enter agents (comma-separated, or Enter for default)",
                    default="",
                )
                agent_ids = parse_agents(agents_input) if agents_input else None
                if agent_ids:
                    agent_ids = validate_agents(agent_ids)

                meeting = Meeting(
                    meeting_type="strategy",
                    topic=topic,
                    agent_ids=agent_ids,
                    console=console,
                )
                meeting.run_discussion(progress_callback=show_progress)

            elif choice == "11":
                # Custom meeting
                topic = Prompt.ask("Enter meeting topic")
                agents_input = Prompt.ask(
                    "Enter agents (comma-separated, or Enter for default)",
                    default="",
                )
                agent_ids = parse_agents(agents_input) if agents_input else None
                if agent_ids:
                    agent_ids = validate_agents(agent_ids)

                meeting = Meeting(
                    meeting_type="custom",
                    topic=topic,
                    agent_ids=agent_ids,
                    console=console,
                )
                meeting.run_discussion(progress_callback=show_progress)

            elif choice == "12":
                # View meetings
                meetings_list = list_meetings(limit=10)
                if not meetings_list:
                    console.print("[yellow]No meetings found.[/yellow]")
                else:
                    table = Table(title="Recent Meetings")
                    table.add_column("#")
                    table.add_column("Date")
                    table.add_column("Type")
                    table.add_column("Topic")

                    for i, m in enumerate(meetings_list, 1):
                        table.add_row(str(i), m["date"], m["type"], m["topic"][:40])

                    console.print(table)

                    view_choice = Prompt.ask(
                        "Enter number to view (or Enter to skip)",
                        default="",
                    )
                    if view_choice.isdigit():
                        idx = int(view_choice) - 1
                        if 0 <= idx < len(meetings_list):
                            content = load_file(meetings_list[idx]["path"])
                            console.print()
                            console.print(Markdown(content))

            elif choice == "13":
                # View decisions
                results = query_decisions(limit=10)
                if not results:
                    console.print("[yellow]No decisions found.[/yellow]")
                else:
                    table = Table(title="Recent Decisions")
                    table.add_column("ID", style="dim")
                    table.add_column("Date")
                    table.add_column("Topic")
                    table.add_column("Decision")
                    table.add_column("Status")

                    for d in results:
                        table.add_row(
                            str(d.get("id", "")),
                            d.get("date", ""),
                            d.get("topic", "")[:25],
                            d.get("decision", "")[:35],
                            d.get("status", ""),
                        )

                    console.print(table)

            elif choice == "14":
                # Company status
                console.print()
                console.print(
                    Panel(
                        "[bold cyan]Rinse Repeat Labs[/bold cyan] — Company Dashboard",
                        border_style="cyan",
                    )
                )
                console.print()

                console.print(f"[bold]Agents:[/bold] {len(available_agents)} active")
                console.print(f"  Executive: {len([a for a in available_agents if a in config.EXECUTIVE_TEAM])}")
                console.print(f"  Technical: {len([a for a in available_agents if a in config.TECHNICAL_TEAM])}")
                console.print(f"  Operations: {len([a for a in available_agents if a not in config.EXECUTIVE_TEAM and a not in config.TECHNICAL_TEAM])}")
                console.print()

                recent_meetings = list_meetings(limit=5)
                if recent_meetings:
                    console.print("[bold]Recent Meetings:[/bold]")
                    for m in recent_meetings:
                        console.print(f"  {m['date']} - {m['type']} - {m['topic'][:40]}")
                console.print()

                recent_decisions = query_decisions(limit=5)
                if recent_decisions:
                    console.print("[bold]Recent Decisions:[/bold]")
                    for d in recent_decisions:
                        console.print(f"  {d.get('topic', '')[:30]} - {d.get('decision', '')[:30]}")

            elif choice == "15":
                # List agents
                def print_agent_table(title: str, agent_list: list[str]):
                    if not agent_list:
                        return
                    table = Table(title=title)
                    table.add_column("ID")
                    table.add_column("Name")
                    table.add_column("Role")

                    for agent_id in agent_list:
                        if agent_id in available_agents:
                            try:
                                agent = registry.get(agent_id)
                                table.add_row(
                                    agent_id,
                                    agent.display_name,
                                    agent.role[:50] if agent.role else "",
                                )
                            except Exception as e:
                                table.add_row(agent_id, "[error]", str(e)[:40])

                    console.print(table)
                    console.print()

                print_agent_table("Executive Team", config.EXECUTIVE_TEAM)
                print_agent_table("Technical Team", config.TECHNICAL_TEAM)
                print_agent_table("Operations Team", config.OPERATIONS_TEAM)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue


# =============================================================================
# SETUP WIZARD
# =============================================================================

@cli.command()
@click.option(
    "--skip-api",
    is_flag=True,
    help="Skip API key configuration",
)
@click.option(
    "--launch-web",
    is_flag=True,
    help="Launch web dashboard after setup",
)
def setup(skip_api: bool, launch_web: bool):
    """First-time setup wizard for Rinse Repeat Labs.

    Guides you through:
    - API key configuration
    - Creating data directories
    - Verifying agent prompts
    - Optionally launching the web dashboard

    Examples:
        python orchestrator.py setup
        python orchestrator.py setup --launch-web
    """
    import os
    import subprocess

    console.print()
    console.print(
        Panel(
            "[bold cyan]Rinse Repeat Labs[/bold cyan] — Setup Wizard\n"
            "   Let's get you started, Architect.",
            border_style="cyan",
        )
    )
    console.print()

    # Step 1: Check/Create directories
    console.print("[bold]Step 1: Checking directories...[/bold]")
    data_dir = config.BASE_DIR / "data"
    meetings_dir = config.MEETINGS_DIR
    reports_dir = config.BASE_DIR / "reports"

    for dir_path in [data_dir, meetings_dir, reports_dir]:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"  [green]Created:[/green] {dir_path}")
        else:
            console.print(f"  [dim]Exists:[/dim] {dir_path}")
    console.print()

    # Step 2: Check API key
    if not skip_api:
        console.print("[bold]Step 2: API Key Configuration...[/bold]")
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")

        if api_key:
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            console.print(f"  [green]Found:[/green] ANTHROPIC_API_KEY ({masked})")
        else:
            console.print("  [yellow]Not found:[/yellow] ANTHROPIC_API_KEY")
            console.print()
            console.print("  To set your API key, run:")
            console.print("  [cyan]export ANTHROPIC_API_KEY='your-key-here'[/cyan]")
            console.print()
            console.print("  Or add to your shell profile (~/.bashrc, ~/.zshrc)")

            new_key = Prompt.ask(
                "  Enter API key now (or press Enter to skip)",
                default="",
                password=True,
            )
            if new_key:
                os.environ["ANTHROPIC_API_KEY"] = new_key
                console.print("  [green]API key set for this session[/green]")
    else:
        console.print("[bold]Step 2: API Key Configuration...[/bold] [dim](skipped)[/dim]")
    console.print()

    # Step 3: Verify agents
    console.print("[bold]Step 3: Verifying agent prompts...[/bold]")
    registry = AgentRegistry()
    available = registry.list_available()
    console.print(f"  [green]Found {len(available)} agents:[/green]")

    # Group by team
    exec_count = len([a for a in available if a in config.EXECUTIVE_TEAM])
    tech_count = len([a for a in available if a in config.TECHNICAL_TEAM])
    ops_count = len(available) - exec_count - tech_count

    console.print(f"    Executive: {exec_count}")
    console.print(f"    Technical: {tech_count}")
    console.print(f"    Operations: {ops_count}")
    console.print()

    # Step 4: Check data stores
    console.print("[bold]Step 4: Initializing data stores...[/bold]")
    from src.data_store import (
        get_ideas_store, get_testers_store, get_clients_store,
        get_projects_store, get_finances_store, get_agent_requests_store
    )

    stores = [
        ("Ideas", get_ideas_store),
        ("Testers", get_testers_store),
        ("Clients", get_clients_store),
        ("Projects", get_projects_store),
        ("Finances", get_finances_store),
        ("Agent Requests", get_agent_requests_store),
    ]

    for name, get_store in stores:
        store = get_store()
        count = len(store.get_all())
        console.print(f"  [green]{name}:[/green] {count} records")
    console.print()

    # Done!
    console.print(
        Panel(
            "[bold green]Setup Complete![/bold green]\n\n"
            "Quick start commands:\n"
            "  [cyan]python orchestrator.py interactive[/cyan] — Interactive menu\n"
            "  [cyan]python orchestrator.py ceo-sync[/cyan] — Meet with the CEO\n"
            "  [cyan]python orchestrator.py status[/cyan] — Company dashboard\n"
            "  [cyan]python start.py[/cyan] — Launch web dashboard\n",
            border_style="green",
        )
    )

    # Launch web if requested
    if launch_web:
        console.print()
        console.print("[bold]Launching web dashboard...[/bold]")
        subprocess.Popen(
            [sys.executable, "start.py"],
            cwd=config.BASE_DIR,
        )
        console.print("[green]Web dashboard starting at http://localhost:5000[/green]")


# Register data management command groups
cli.add_command(ideas)
cli.add_command(testers)
cli.add_command(clients)
cli.add_command(projects)
cli.add_command(finances)
cli.add_command(report)
cli.add_command(requests)


if __name__ == "__main__":
    cli()
