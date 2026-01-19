"""Meeting facilitation logic for the Rinse Repeat Labs Agent Orchestrator."""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

import config
from src.agent import Agent, AgentRegistry
from src.utils import (
    load_context,
    save_meeting_transcript,
    save_decision,
    format_timestamp,
    format_date,
    load_file,
)


class Meeting:
    """Facilitates a meeting between multiple agents."""

    def __init__(
        self,
        meeting_type: str,
        topic: str,
        agent_ids: list[str] | None = None,
        facilitator_id: str | None = None,
        registry: AgentRegistry | None = None,
        console: Console | None = None,
    ):
        """Initialize a meeting.

        Args:
            meeting_type: Type of meeting (standup, strategy, idea_review, retro, custom, etc.)
            topic: Meeting topic or agenda
            agent_ids: List of agent IDs to include (defaults to meeting type config)
            facilitator_id: ID of facilitating agent (defaults to meeting type config)
            registry: Agent registry to use
            console: Rich console for output
        """
        self.meeting_type = meeting_type
        self.topic = topic
        self.console = console or Console()
        self.registry = registry or AgentRegistry()

        # Get meeting type configuration
        type_config = config.MEETING_TYPES.get(
            meeting_type, config.MEETING_TYPES["custom"]
        )

        # Set agents and facilitator
        self.agent_ids = agent_ids or type_config["default_agents"]
        self.facilitator_id = facilitator_id or type_config["facilitator"]
        self.context_types = type_config.get("include_context", ["company"])

        # Meeting state
        self.started_at: datetime | None = None
        self.responses: list[dict[str, str]] = []
        self.decisions: list[dict[str, Any]] = []
        self.action_items: list[dict[str, str]] = []
        self.synthesis: str = ""

    def _load_context(self, extra_context: str = "") -> str:
        """Load context for the meeting."""
        context = load_context(self.context_types)
        if extra_context:
            context = f"{context}\n\n---\n\n{extra_context}"
        return context

    def _build_prior_discussion(self) -> str:
        """Build a summary of prior discussion for context."""
        if not self.responses:
            return ""

        parts = []
        for response in self.responses:
            parts.append(f"### {response['agent_name']}\n{response['response']}")

        return "\n\n".join(parts)

    def _display_response(self, agent: Agent, response: str) -> None:
        """Display an agent's response."""
        self.console.print()
        self.console.print(
            Panel(
                Markdown(response),
                title=f"[bold cyan]{agent.display_name}[/bold cyan]",
                border_style="cyan",
            )
        )

    def run_standup(self, progress_callback: Callable[[str], None] | None = None) -> str:
        """Run a standup meeting.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        self.started_at = datetime.now()
        context = self._load_context()

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Daily Standup[/bold]\n{format_timestamp(self.started_at)}",
                border_style="green",
            )
        )

        # Get update from each agent
        for agent_id in self.agent_ids:
            if progress_callback:
                progress_callback(f"Getting update from {agent_id}...")

            agent = self.registry.get(agent_id)
            response = agent.get_standup_update(context=context)

            self.responses.append({
                "agent_id": agent_id,
                "agent_name": agent.display_name,
                "response": response,
            })

            self._display_response(agent, response)

        # Generate transcript
        return self._generate_transcript("Daily Standup")

    def run_one_on_one(
        self,
        topic: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Run a 1:1 meeting with the Architect and one agent.

        This is an interactive conversation where the agent provides their perspective
        and is ready to discuss with the Architect.

        Args:
            topic: Specific topic to discuss (optional)
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        self.started_at = datetime.now()
        context = self._load_context()

        agent_id = self.agent_ids[0]
        agent = self.registry.get(agent_id)

        meeting_name = config.MEETING_TYPES.get(
            self.meeting_type, {}
        ).get("name", "1:1 Meeting")

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]{meeting_name}[/bold]\n"
                f"Agent: {agent.display_name}\n"
                f"Topic: {self.topic}\n"
                f"{format_timestamp(self.started_at)}",
                border_style="green",
            )
        )

        if progress_callback:
            progress_callback(f"Getting response from {agent_id}...")

        # Build a prompt tailored for 1:1 meetings
        if topic:
            prompt = f"""You are having a 1:1 meeting with the Architect (the human principal who oversees Rinse Repeat Labs).

**Topic:** {topic}

Please provide your perspective on this topic. Include:
- Your current assessment and key observations
- Any updates relevant to your role
- Concerns or risks you want to highlight
- Recommendations or suggestions
- Questions you have for the Architect

Be direct and thorough. This is your opportunity to share insights from your domain."""
        else:
            prompt = f"""You are having a 1:1 meeting with the Architect (the human principal who oversees Rinse Repeat Labs).

Please provide a comprehensive update from your role. Include:
- Current status and priorities in your domain
- Key accomplishments and progress
- Challenges or blockers you're facing
- Risks or concerns on your radar
- Items that need the Architect's attention or decision
- Questions or topics you'd like to discuss

Be direct and thorough. This is your opportunity to share your perspective."""

        response = agent.respond(prompt=prompt, context=context)

        self.responses.append({
            "agent_id": agent_id,
            "agent_name": agent.display_name,
            "response": response,
        })

        self._display_response(agent, response)

        # Generate transcript (no synthesis for 1:1s)
        return self._generate_one_on_one_transcript(meeting_name, agent)

    def run_discussion(
        self,
        prompt: str | None = None,
        extra_context: str = "",
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Run a discussion meeting (strategy, custom, etc.).

        Args:
            prompt: Custom prompt for the discussion (defaults to topic)
            extra_context: Additional context to include
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        self.started_at = datetime.now()
        context = self._load_context(extra_context)

        meeting_name = config.MEETING_TYPES.get(
            self.meeting_type, {}
        ).get("name", "Meeting")

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]{meeting_name}[/bold]\n"
                f"Topic: {self.topic}\n"
                f"Participants: {', '.join(config.AGENT_DISPLAY_NAMES.get(a, a) for a in self.agent_ids)}\n"
                f"{format_timestamp(self.started_at)}",
                border_style="green",
            )
        )

        discussion_prompt = prompt or f"""We are having a {meeting_name.lower()} to discuss:

**{self.topic}**

Please share your perspective on this topic from your role. Consider:
- Key points relevant to your expertise
- Potential concerns or risks
- Recommendations or suggestions
- Questions that need to be addressed

Be specific and actionable in your response."""

        # Get response from each agent
        for agent_id in self.agent_ids:
            if progress_callback:
                progress_callback(f"Getting input from {agent_id}...")

            agent = self.registry.get(agent_id)
            prior_discussion = self._build_prior_discussion()

            response = agent.respond(
                prompt=discussion_prompt,
                context=context,
                prior_discussion=prior_discussion,
            )

            self.responses.append({
                "agent_id": agent_id,
                "agent_name": agent.display_name,
                "response": response,
            })

            self._display_response(agent, response)

        # Get synthesis from facilitator
        if progress_callback:
            progress_callback(f"Getting synthesis from {self.facilitator_id}...")

        self._generate_synthesis(context)

        # Generate transcript
        return self._generate_transcript(meeting_name)

    def run_project_meeting(
        self,
        project: str,
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Run a project-specific meeting.

        Args:
            project: Name of the project
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        extra_context = f"## Project Focus\n\nThis meeting is focused on the **{project}** project."

        prompt = f"""We are having a project meeting focused on **{project}**.

**Meeting Topic:** {self.topic}

Please provide your update and perspective on this project from your role:
- Current status and progress in your area
- Blockers or dependencies
- Risks or concerns
- What you need from other team members
- Questions or decisions needed

Be specific to this project and focus on actionable items."""

        return self.run_discussion(
            prompt=prompt,
            extra_context=extra_context,
            progress_callback=progress_callback,
        )

    def run_idea_review(
        self,
        idea_file: str | Path | None = None,
        idea_content: str | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Run an idea review meeting.

        Args:
            idea_file: Path to idea file to review
            idea_content: Direct idea content (alternative to file)
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        # Load idea content
        if idea_file:
            idea_path = Path(idea_file)
            idea_content = load_file(idea_path)
            if not idea_content:
                raise FileNotFoundError(f"Idea file not found or empty: {idea_file}")

        if not idea_content:
            raise ValueError("Either idea_file or idea_content must be provided")

        extra_context = f"## Idea Under Review\n\n{idea_content}"

        # Role-specific evaluation prompts
        role_prompts = {
            "cito": """Evaluate the **technical feasibility** of this idea:
- Is it technically possible with current technology?
- What technology stack would you recommend?
- What are the technical risks and unknowns?
- Estimate complexity: Simple / Moderate / Complex / Very Complex
- What third-party dependencies would be needed?
- Your recommendation: Proceed / Modify / Pass""",

            "cfo": """Evaluate the **financial aspects** of this idea:
- What's the estimated cost range to build?
- Which revenue model would you recommend (Full Payment, 70/30, 50/50)?
- What's the profitability potential?
- Cash flow implications?
- Your recommendation: Proceed / Modify / Pass""",

            "sales": """Evaluate the **client fit and deal potential**:
- Does this align with our target market?
- What's the competitive landscape?
- How strong is the market opportunity?
- Any concerns about the client or deal structure?
- Your recommendation: Proceed / Modify / Pass""",

            "legal": """Evaluate the **legal considerations**:
- Any compliance requirements (GDPR, CCPA, HIPAA)?
- IP ownership considerations?
- Contract terms to be aware of?
- Potential legal risks?
- Your recommendation: Proceed / Modify / Pass""",

            "pm": """Evaluate the **project timeline and resources**:
- Estimated timeline range?
- What resources would be needed?
- Dependencies and critical path items?
- Risks to delivery?
- Your recommendation: Proceed / Modify / Pass""",

            "design_lead": """Evaluate the **UX complexity and design effort**:
- How complex is the user experience?
- What user research would be needed?
- Estimated design effort?
- Accessibility considerations?
- Your recommendation: Proceed / Modify / Pass""",
        }

        self.started_at = datetime.now()
        context = self._load_context(extra_context)

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Idea Review[/bold]\n"
                f"Topic: {self.topic}\n"
                f"Participants: {', '.join(config.AGENT_DISPLAY_NAMES.get(a, a) for a in self.agent_ids)}\n"
                f"{format_timestamp(self.started_at)}",
                border_style="green",
            )
        )

        # Get response from each agent with role-specific prompts
        for agent_id in self.agent_ids:
            if progress_callback:
                progress_callback(f"Getting evaluation from {agent_id}...")

            agent = self.registry.get(agent_id)
            prior_discussion = self._build_prior_discussion()

            # Use role-specific prompt if available
            role_prompt = role_prompts.get(
                agent_id,
                f"""Evaluate this idea from your role's perspective:
- Feasibility and complexity in your area
- Potential risks and concerns
- Resource and timeline implications
- Your recommendation: Proceed / Modify / Pass"""
            )

            prompt = f"""We are reviewing a new idea/proposal for potential development.

**Idea Summary:**
{self.topic}

**Full Proposal:**
{idea_content}

{role_prompt}

Be specific and provide clear rationale for your assessment."""

            response = agent.respond(
                prompt=prompt,
                context=context,
                prior_discussion=prior_discussion,
            )

            self.responses.append({
                "agent_id": agent_id,
                "agent_name": agent.display_name,
                "response": response,
            })

            self._display_response(agent, response)

        # Get synthesis from facilitator
        if progress_callback:
            progress_callback(f"Getting synthesis from {self.facilitator_id}...")

        self._generate_idea_synthesis(context, idea_content)

        # Generate transcript
        return self._generate_transcript("Idea Review")

    def run_retrospective(
        self,
        project: str,
        progress_callback: Callable[[str], None] | None = None,
    ) -> str:
        """Run a project retrospective.

        Args:
            project: Name of the project to review
            progress_callback: Optional callback for progress updates

        Returns:
            The meeting transcript.
        """
        prompt = f"""We are running a retrospective for the project: **{project}**

Please reflect on this project from your role's perspective and share:

**What went well:**
- Things that worked effectively
- Successes worth celebrating

**What didn't go well:**
- Challenges and pain points
- Things that should have been done differently

**Lessons learned:**
- Key takeaways for future projects
- Process improvements to implement

**Action items:**
- Specific things to change going forward

Be honest and constructive. The goal is continuous improvement."""

        return self.run_discussion(prompt=prompt, progress_callback=progress_callback)

    def _generate_synthesis(self, context: str) -> None:
        """Generate a synthesis of the discussion from the facilitator."""
        facilitator = self.registry.get(self.facilitator_id)
        prior_discussion = self._build_prior_discussion()

        synthesis_prompt = f"""As the facilitator of this meeting, please synthesize the discussion.

**Meeting Topic:** {self.topic}

Please provide:

## Summary
A brief summary of the key points discussed.

## Decisions
List any decisions that were made or need to be made. Format as:
- **Decision:** [What was decided]
  - **Rationale:** [Why]
  - **Owner:** [Who is responsible]

## Action Items
List specific action items. Format as:
- [ ] @[Owner]: [Action item description]

## Next Steps
Any follow-up meetings or activities needed.

Be specific and ensure all action items have clear owners."""

        self.synthesis = facilitator.respond(
            prompt=synthesis_prompt,
            context=context,
            prior_discussion=prior_discussion,
        )

        self.console.print()
        self.console.print(
            Panel(
                Markdown(self.synthesis),
                title=f"[bold green]Synthesis by {facilitator.display_name}[/bold green]",
                border_style="green",
            )
        )

    def _generate_idea_synthesis(self, context: str, idea_content: str) -> None:
        """Generate a synthesis specifically for idea reviews."""
        facilitator = self.registry.get(self.facilitator_id)
        prior_discussion = self._build_prior_discussion()

        synthesis_prompt = f"""As the facilitator of this idea review, synthesize all evaluations.

**Idea:** {self.topic}

Please provide:

## Executive Summary
One paragraph summary of the idea and overall assessment.

## Go/No-Go Recommendation
Based on all perspectives, provide a clear recommendation:
- **Recommendation:** [GO / GO WITH MODIFICATIONS / NO-GO]
- **Confidence Level:** [High / Medium / Low]
- **Key Rationale:** [Why this recommendation]

## Technical Assessment Summary
- Stack recommendation
- Complexity level
- Key technical risks

## Financial Assessment Summary
- Recommended revenue model
- Estimated cost range
- Profitability outlook

## Timeline Estimate
- Estimated duration
- Key milestones

## Key Concerns
List the top concerns that must be addressed.

## Next Steps
If GO: What needs to happen next?
If NO-GO: What would need to change for reconsideration?

Be decisive and actionable."""

        self.synthesis = facilitator.respond(
            prompt=synthesis_prompt,
            context=context,
            prior_discussion=prior_discussion,
        )

        self.console.print()
        self.console.print(
            Panel(
                Markdown(self.synthesis),
                title=f"[bold green]Idea Review Summary by {facilitator.display_name}[/bold green]",
                border_style="green",
            )
        )

    def _generate_transcript(self, meeting_name: str) -> str:
        """Generate a markdown transcript of the meeting."""
        timestamp = format_timestamp(self.started_at)
        date_str = format_date(self.started_at)

        participants = ", ".join(
            self.registry.get(aid).display_name for aid in self.agent_ids
        )
        facilitator_name = self.registry.get(self.facilitator_id).display_name

        lines = [
            f"# {meeting_name}: {self.topic}",
            f"**Date:** {date_str}",
            f"**Participants:** {participants}",
            f"**Facilitator:** {facilitator_name}",
            "",
            "---",
            "",
            "## Agenda",
            self.topic,
            "",
            "---",
            "",
            "## Discussion",
            "",
        ]

        # Add each agent's response
        for response in self.responses:
            lines.extend([
                f"### {response['agent_name']}",
                response["response"],
                "",
            ])

        # Add synthesis if present
        if self.synthesis:
            lines.extend([
                "---",
                "",
                f"## Synthesis (by {facilitator_name})",
                self.synthesis,
                "",
            ])

        lines.extend([
            "---",
            "",
            "*Meeting generated by Rinse Repeat Labs Orchestrator*",
        ])

        transcript = "\n".join(lines)

        # Save the transcript
        file_path = save_meeting_transcript(
            meeting_type=self.meeting_type,
            topic=self.topic,
            content=transcript,
            dt=self.started_at,
        )

        self.console.print()
        self.console.print(f"[dim]Transcript saved to: {file_path}[/dim]")

        return transcript

    def _generate_one_on_one_transcript(self, meeting_name: str, agent: Agent) -> str:
        """Generate a transcript for 1:1 meetings (no synthesis needed)."""
        timestamp = format_timestamp(self.started_at)
        date_str = format_date(self.started_at)

        lines = [
            f"# {meeting_name}: {self.topic}",
            f"**Date:** {date_str}",
            f"**Participant:** {agent.display_name}",
            "",
            "---",
            "",
            "## Discussion",
            "",
            f"### {agent.display_name}",
            self.responses[0]["response"] if self.responses else "",
            "",
            "---",
            "",
            "*1:1 Meeting generated by Rinse Repeat Labs Orchestrator*",
        ]

        transcript = "\n".join(lines)

        # Save the transcript
        file_path = save_meeting_transcript(
            meeting_type=self.meeting_type,
            topic=self.topic,
            content=transcript,
            dt=self.started_at,
        )

        self.console.print()
        self.console.print(f"[dim]Transcript saved to: {file_path}[/dim]")

        return transcript

    def add_decision(
        self,
        decision: str,
        rationale: str,
        owner: str,
        status: str = "pending",
    ) -> None:
        """Add a decision from this meeting.

        Args:
            decision: The decision made
            rationale: Why this decision was made
            owner: Who is responsible
            status: Current status
        """
        decision_record = {
            "date": format_date(self.started_at or datetime.now()),
            "topic": self.topic,
            "decision": decision,
            "rationale": rationale,
            "owner": owner,
            "status": status,
            "meeting_type": self.meeting_type,
        }

        self.decisions.append(decision_record)
        save_decision(decision_record)
