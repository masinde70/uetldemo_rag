"""Agent Orchestrator for routing queries to specialized agents.

Provides:
- Automatic routing based on mode/query
- Agent registration and management
- Multi-agent coordination for complex queries
"""

from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.base import AgentResponse, BaseAgent
from backend.agents.strategy import StrategyAgent
from backend.agents.actions import ActionsAgent
from backend.agents.analytics import AnalyticsAgent
from backend.agents.regulatory import RegulatoryAgent


# Mode to agent mapping
MODE_AGENT_MAP: dict[str, Type[BaseAgent]] = {
    "strategy_qa": StrategyAgent,
    "actions": ActionsAgent,
    "analytics": AnalyticsAgent,
    "regulatory": RegulatoryAgent,
}


def get_agent_for_mode(mode: str, db: AsyncSession) -> BaseAgent:
    """Get the appropriate agent for a given mode.

    Args:
        mode: The chat mode
        db: Database session

    Returns:
        Instantiated agent for the mode

    Raises:
        ValueError: If mode is not supported
    """
    agent_class = MODE_AGENT_MAP.get(mode)
    if agent_class is None:
        raise ValueError(f"Unsupported mode: {mode}. Supported: {list(MODE_AGENT_MAP.keys())}")

    return agent_class(db)


async def route_to_agent(
    query: str,
    mode: str,
    db: AsyncSession,
    history: Optional[list[dict]] = None,
) -> AgentResponse:
    """Route a query to the appropriate agent and get response.

    This is the main entry point for using the multi-agent system.

    Args:
        query: User query
        mode: Chat mode determining which agent handles the query
        db: Database session
        history: Optional conversation history

    Returns:
        AgentResponse from the specialized agent
    """
    agent = get_agent_for_mode(mode, db)
    return await agent.process(query, history)


class AgentOrchestrator:
    """Orchestrator for managing multiple agents.

    Provides advanced features like:
    - Agent coordination
    - Multi-agent queries
    - Response aggregation
    """

    def __init__(self, db: AsyncSession):
        """Initialize orchestrator with database session.

        Args:
            db: Async database session
        """
        self.db = db
        self._agents: dict[str, BaseAgent] = {}

    def get_agent(self, mode: str) -> BaseAgent:
        """Get or create agent for a mode.

        Args:
            mode: The chat mode

        Returns:
            Agent instance (cached)
        """
        if mode not in self._agents:
            self._agents[mode] = get_agent_for_mode(mode, self.db)
        return self._agents[mode]

    async def process(
        self,
        query: str,
        mode: str,
        history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """Process a query with the appropriate agent.

        Args:
            query: User query
            mode: Chat mode
            history: Conversation history

        Returns:
            AgentResponse from the agent
        """
        agent = self.get_agent(mode)
        return await agent.process(query, history)

    async def multi_agent_query(
        self,
        query: str,
        modes: list[str],
        history: Optional[list[dict]] = None,
    ) -> dict[str, AgentResponse]:
        """Query multiple agents and collect responses.

        Useful for complex queries that span multiple domains.

        Args:
            query: User query
            modes: List of modes/agents to query
            history: Conversation history

        Returns:
            Dict mapping mode to AgentResponse
        """
        import asyncio

        async def query_agent(mode: str) -> tuple[str, AgentResponse]:
            agent = self.get_agent(mode)
            response = await agent.process(query, history)
            return mode, response

        tasks = [query_agent(mode) for mode in modes]
        results = await asyncio.gather(*tasks)

        return dict(results)

    async def synthesize_responses(
        self,
        responses: dict[str, AgentResponse],
        query: str,
    ) -> str:
        """Synthesize multiple agent responses into one.

        Args:
            responses: Dict of agent responses
            query: Original query

        Returns:
            Synthesized response combining insights from all agents
        """
        # Build synthesis prompt
        parts = [f"Original Question: {query}\n"]
        parts.append("Agent Responses:\n")

        for mode, response in responses.items():
            parts.append(f"## {mode.upper()} Agent:")
            parts.append(response.answer)
            parts.append("")

        # Use strategy agent for synthesis (could be a dedicated synthesizer)
        from backend.services.llm import chat_completion

        synthesis_prompt = """You are synthesizing responses from multiple specialized agents.
Combine the insights into a coherent, comprehensive response.
Highlight areas of agreement and note any complementary perspectives.
Do not simply concatenate - create a unified answer."""

        combined_context = "\n".join(parts)

        return await chat_completion(
            messages=[{"role": "user", "content": "Please synthesize these responses."}],
            system_prompt=synthesis_prompt,
            context=combined_context,
        )

    @property
    def available_agents(self) -> dict[str, str]:
        """Get available agents and their descriptions.

        Returns:
            Dict mapping mode to agent description
        """
        return {
            mode: agent_class.description
            for mode, agent_class in MODE_AGENT_MAP.items()
        }
