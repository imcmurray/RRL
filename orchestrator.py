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

console = Console()


def parse_agents(agents_str: str | None) -> list[str] | None:
    """Parse comma-separated agent string into list."""
    if not agents_str:
        return None
    return [a.strip().lower() for a in agents_str.split(",")]


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
@click.version_option(version="1.0.0")
def cli():
    """Rinse Repeat Labs Agent Orchestrator

    Coordinate AI agents in virtual meetings for planning, strategy, and decision-making.
    """
    pass


@cli.command()
@click.option(
    "--agents",
    "-a",
    help="Comma-separated list of agents (default: all)",
)
def standup(agents: str | None):
    """Run a daily standup meeting."""
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
    help="Facilitator agent ID (default: cito)",
)
def strategy(topic: str, agents: str | None, facilitator: str | None):
    """Run a strategy session on a specific topic."""
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
    help="Comma-separated list of agents",
)
def idea_review(idea: str, agents: str | None):
    """Review a new idea or proposal."""
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
    help="Comma-separated list of agents",
)
def retro(project: str, agents: str | None):
    """Run a project retrospective."""
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
    """Run a custom meeting on any topic."""
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
    """View and filter past decisions."""
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
    """List available agents."""
    registry = AgentRegistry()
    available = registry.list_available()

    table = Table(title="Available Agents")
    table.add_column("ID")
    table.add_column("Display Name")
    table.add_column("Role")

    for agent_id in available:
        try:
            agent = registry.get(agent_id)
            table.add_row(
                agent_id,
                agent.display_name,
                agent.role[:60] if agent.role else "",
            )
        except Exception as e:
            table.add_row(agent_id, "[error]", str(e)[:40])

    console.print(table)


@cli.command()
def interactive():
    """Run in interactive mode with a menu."""
    registry = AgentRegistry()
    available_agents = registry.list_available()

    while True:
        console.print()
        console.print(
            Panel(
                "[bold cyan]Rinse Repeat Labs[/bold cyan] — Agent Orchestrator",
                border_style="cyan",
            )
        )
        console.print()
        console.print("What would you like to do?")
        console.print()
        console.print("  [bold]1.[/bold] Run a standup")
        console.print("  [bold]2.[/bold] Strategy session")
        console.print("  [bold]3.[/bold] Review an idea")
        console.print("  [bold]4.[/bold] Project retrospective")
        console.print("  [bold]5.[/bold] Custom meeting")
        console.print("  [bold]6.[/bold] View past meetings")
        console.print("  [bold]7.[/bold] View decisions")
        console.print("  [bold]8.[/bold] List agents")
        console.print("  [bold]9.[/bold] Exit")
        console.print()

        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

        try:
            if choice == "1":
                # Standup
                meeting = Meeting(
                    meeting_type="standup",
                    topic="Daily Standup",
                    console=console,
                )
                meeting.run_standup(progress_callback=show_progress)

            elif choice == "2":
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

            elif choice == "3":
                # Idea review
                idea_path = Prompt.ask("Enter path to idea file")
                if not Path(idea_path).exists():
                    console.print(f"[red]File not found: {idea_path}[/red]")
                    continue

                idea_content = load_file(Path(idea_path))
                topic = Path(idea_path).stem.replace("-", " ").replace("_", " ").title()

                meeting = Meeting(
                    meeting_type="idea_review",
                    topic=f"Idea Review: {topic}",
                    console=console,
                )
                meeting.run_idea_review(idea_file=idea_path, progress_callback=show_progress)

            elif choice == "4":
                # Retrospective
                project = Prompt.ask("Enter project name")
                meeting = Meeting(
                    meeting_type="retro",
                    topic=f"Retrospective: {project}",
                    console=console,
                )
                meeting.run_retrospective(project=project, progress_callback=show_progress)

            elif choice == "5":
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

            elif choice == "6":
                # View meetings
                meetings = list_meetings(limit=10)
                if not meetings:
                    console.print("[yellow]No meetings found.[/yellow]")
                else:
                    table = Table(title="Recent Meetings")
                    table.add_column("#")
                    table.add_column("Date")
                    table.add_column("Type")
                    table.add_column("Topic")

                    for i, m in enumerate(meetings, 1):
                        table.add_row(str(i), m["date"], m["type"], m["topic"][:40])

                    console.print(table)

                    view_choice = Prompt.ask(
                        "Enter number to view (or Enter to skip)",
                        default="",
                    )
                    if view_choice.isdigit():
                        idx = int(view_choice) - 1
                        if 0 <= idx < len(meetings):
                            content = load_file(meetings[idx]["path"])
                            console.print()
                            console.print(Markdown(content))

            elif choice == "7":
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

            elif choice == "8":
                # List agents
                table = Table(title="Available Agents")
                table.add_column("ID")
                table.add_column("Name")
                table.add_column("Role")

                for agent_id in available_agents:
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

            elif choice == "9":
                console.print("[cyan]Goodbye![/cyan]")
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue


if __name__ == "__main__":
    cli()
