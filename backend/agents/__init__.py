"""Multi-Agent Architecture for SISUiQ.

This module provides a collection of specialized agents for different tasks:
- StrategyAgent: Answers strategic planning questions
- ActionsAgent: Generates actionable recommendations
- AnalyticsAgent: Analyzes operational data
- RegulatoryAgent: Handles ERA compliance queries

Each agent has specialized prompts and retrieval strategies optimized
for their domain.
"""

from backend.agents.base import BaseAgent, AgentResponse
from backend.agents.strategy import StrategyAgent
from backend.agents.actions import ActionsAgent
from backend.agents.analytics import AnalyticsAgent
from backend.agents.regulatory import RegulatoryAgent
from backend.agents.orchestrator import AgentOrchestrator, route_to_agent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "StrategyAgent",
    "ActionsAgent",
    "AnalyticsAgent",
    "RegulatoryAgent",
    "AgentOrchestrator",
    "route_to_agent",
]
