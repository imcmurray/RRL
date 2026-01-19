"""Agent class for the Rinse Repeat Labs Agent Orchestrator."""

from pathlib import Path
from typing import Any

import anthropic

import config
from src.utils import parse_agent_markdown, load_file


class Agent:
    """Represents an AI agent with a specific role and persona."""

    def __init__(
        self,
        agent_id: str,
        client: anthropic.Anthropic | None = None,
    ):
        """Initialize an agent.

        Args:
            agent_id: The agent identifier (e.g., "cito", "pm")
            client: Optional Anthropic client (creates one if not provided)
        """
        self.agent_id = agent_id
        self.client = client or anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

        # Load agent configuration from markdown file
        self._load_config()

    def _load_config(self) -> None:
        """Load agent configuration from its markdown file."""
        agent_file = config.AGENTS_DIR / f"{self.agent_id}.md"

        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        content = load_file(agent_file)
        parsed = parse_agent_markdown(content)

        self.name = parsed["name"] or self.agent_id.upper()
        self.role = parsed["role"]
        self.expertise = parsed["expertise"]
        self.responsibilities = parsed["responsibilities"]
        self.communication_style = parsed["communication_style"]
        self.system_prompt = parsed["system_prompt"]

        # Set display name from config or use parsed name
        self.display_name = config.AGENT_DISPLAY_NAMES.get(self.agent_id, self.name)

    def respond(
        self,
        prompt: str,
        context: str = "",
        prior_discussion: str = "",
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Get a response from this agent.

        Args:
            prompt: The main prompt/question for the agent
            context: Shared context to include (company info, projects, etc.)
            prior_discussion: Previous discussion in the meeting to reference
            model: Model to use (defaults to config.DEFAULT_MODEL)
            max_tokens: Max tokens for response (defaults to config.MAX_TOKENS)

        Returns:
            The agent's response text.
        """
        model = model or config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS

        # Build the full system prompt
        system_parts = [self.system_prompt]

        if context:
            system_parts.append(f"\n\n## Current Context\n\n{context}")

        full_system = "\n".join(system_parts)

        # Build the user message
        message_parts = []

        if prior_discussion:
            message_parts.append(
                f"## Prior Discussion in This Meeting\n\n{prior_discussion}\n\n---\n\n"
            )

        message_parts.append(prompt)

        full_message = "".join(message_parts)

        # Call the API
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=full_system,
            messages=[{"role": "user", "content": full_message}],
        )

        # Extract text from response
        return response.content[0].text

    def get_standup_update(self, context: str = "") -> str:
        """Get a standup update from this agent.

        Args:
            context: Shared context to include

        Returns:
            The agent's standup update.
        """
        prompt = """Please provide your standup update in the following format:

**Done:** What you've completed recently
**Doing:** What you're currently working on
**Blocked:** Any blockers or issues (or "None" if no blockers)

Be specific and concise. Reference actual projects or initiatives where relevant."""

        return self.respond(prompt, context=context)

    def __repr__(self) -> str:
        return f"Agent(id={self.agent_id!r}, name={self.display_name!r})"


class AgentRegistry:
    """Registry for loading and caching agents."""

    def __init__(self, client: anthropic.Anthropic | None = None):
        """Initialize the registry.

        Args:
            client: Shared Anthropic client for all agents
        """
        self.client = client or anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self._agents: dict[str, Agent] = {}

    def get(self, agent_id: str) -> Agent:
        """Get an agent by ID, loading it if necessary.

        Args:
            agent_id: The agent identifier

        Returns:
            The Agent instance.
        """
        if agent_id not in self._agents:
            self._agents[agent_id] = Agent(agent_id, client=self.client)
        return self._agents[agent_id]

    def get_multiple(self, agent_ids: list[str]) -> list[Agent]:
        """Get multiple agents by ID.

        Args:
            agent_ids: List of agent identifiers

        Returns:
            List of Agent instances.
        """
        return [self.get(agent_id) for agent_id in agent_ids]

    def list_available(self) -> list[str]:
        """List all available agent IDs.

        Returns:
            List of agent IDs (based on files in agents directory).
        """
        agents = []
        if config.AGENTS_DIR.exists():
            for path in config.AGENTS_DIR.glob("*.md"):
                agents.append(path.stem)
        return sorted(agents)

    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self._agents.clear()
