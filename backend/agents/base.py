"""Base agent class for the multi-agent architecture.

Provides common functionality shared by all specialized agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.rag import hybrid_retrieve
from backend.services.llm import chat_completion


@dataclass
class AgentResponse:
    """Response from an agent."""

    answer: str
    sources: list[str]
    agent_name: str
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "agent_name": self.agent_name,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Base class for all specialized agents.

    Each agent has:
    - A unique name
    - A system prompt tailored to their domain
    - Custom retrieval filters
    - Response post-processing
    """

    name: str = "base"
    description: str = "Base agent"

    def __init__(self, db: AsyncSession):
        """Initialize agent with database session.

        Args:
            db: Async database session for queries
        """
        self.db = db

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.

        Returns:
            System prompt string tailored to the agent's domain.
        """
        pass

    def get_retrieval_filters(self) -> Optional[dict]:
        """Get filters for document retrieval.

        Override in subclasses to filter by source type, etc.

        Returns:
            Dict of filters or None for no filtering.
        """
        return None

    def get_top_n(self) -> int:
        """Get number of chunks to retrieve.

        Returns:
            Number of top chunks to retrieve.
        """
        return 8

    async def retrieve_context(self, query: str) -> tuple[list[dict], list[str]]:
        """Retrieve relevant context for the query.

        Args:
            query: User query

        Returns:
            Tuple of (chunks, source citations)
        """
        chunks = await hybrid_retrieve(
            query=query,
            db=self.db,
            top_n=self.get_top_n(),
            filters=self.get_retrieval_filters(),
        )

        # Extract unique sources
        sources = []
        seen = set()
        for chunk in chunks:
            citation = chunk.get("citation", chunk.get("source", ""))
            if citation and citation not in seen:
                sources.append(citation)
                seen.add(citation)

        return chunks, sources

    def build_context_prompt(self, chunks: list[dict]) -> str:
        """Build context prompt from retrieved chunks.

        Args:
            chunks: Retrieved document chunks

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant documents found."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("citation", chunk.get("source", "Unknown"))
            text = chunk.get("text", chunk.get("content", ""))
            context_parts.append(f"[{i}] Source: {source}\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def post_process(self, response: str) -> str:
        """Post-process the LLM response.

        Override in subclasses for custom processing.

        Args:
            response: Raw LLM response

        Returns:
            Processed response
        """
        return response

    async def process(
        self,
        query: str,
        history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """Process a query and generate a response.

        Args:
            query: User query
            history: Optional conversation history

        Returns:
            AgentResponse with answer and metadata
        """
        # Retrieve context
        chunks, sources = await self.retrieve_context(query)

        # Build prompts
        system_prompt = self.get_system_prompt()
        context_prompt = self.build_context_prompt(chunks)

        # Prepare messages
        messages = history or []
        messages.append({"role": "user", "content": query})

        # Generate response
        answer = await chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            context=context_prompt,
        )

        # Post-process
        answer = self.post_process(answer)

        return AgentResponse(
            answer=answer,
            sources=sources,
            agent_name=self.name,
            metadata={
                "chunks_retrieved": len(chunks),
                "context_length": len(context_prompt),
            },
        )
