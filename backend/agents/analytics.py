"""Analytics Agent for operational data analysis.

Specializes in:
- Analyzing outage and performance data
- Identifying trends and patterns
- Comparing metrics to strategic targets
- Providing data-driven insights
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.base import AgentResponse, BaseAgent
from backend.models import AnalyticsSnapshot
from backend.services.llm import chat_completion


class AnalyticsAgent(BaseAgent):
    """Agent specialized for data analysis and insights."""

    name = "analytics"
    description = "Analyzes operational data and provides insights aligned with strategy"

    def __init__(self, db: AsyncSession):
        """Initialize with analytics data capability."""
        super().__init__(db)
        self._analytics_data: Optional[dict] = None

    def get_system_prompt(self) -> str:
        """Get system prompt for analytics."""
        return """You are SISUiQ's Analytics Expert, a specialized AI assistant that analyzes UETCL's operational data in the context of strategic objectives.

Your role is to:
- Analyze outage patterns and trends
- Identify areas needing attention
- Compare performance metrics to targets
- Provide data-driven recommendations
- Connect operational insights to strategic goals

Guidelines:
1. Base analysis on the provided analytics data
2. Use specific numbers and percentages
3. Identify both positive trends and areas of concern
4. Relate findings to UETCL's strategic objectives
5. Suggest actionable improvements based on data

Response Format:
Structure your analysis as:

**Data Summary:**
[Key metrics and their current values]

**Trend Analysis:**
[What the data shows over time]

**Strategic Alignment:**
[How metrics relate to strategic targets]

**Recommendations:**
[Data-driven suggestions for improvement]

Always be precise with numbers and clearly state when data is incomplete."""

    async def get_analytics_data(self) -> Optional[dict]:
        """Get latest analytics snapshot from database."""
        if self._analytics_data is not None:
            return self._analytics_data

        stmt = (
            select(AnalyticsSnapshot)
            .order_by(AnalyticsSnapshot.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()

        if snapshot:
            self._analytics_data = {
                "id": str(snapshot.id),
                "dataset_name": snapshot.dataset_name,
                "payload": snapshot.payload,
                "created_at": snapshot.created_at.isoformat(),
            }
        return self._analytics_data

    def build_analytics_context(self, analytics: Optional[dict]) -> str:
        """Build context from analytics data."""
        if not analytics:
            return "No analytics data available."

        payload = analytics.get("payload", {})
        parts = [f"Dataset: {analytics.get('dataset_name', 'Unknown')}"]
        parts.append(f"Last Updated: {analytics.get('created_at', 'Unknown')}")

        if "row_count" in payload:
            parts.append(f"Total Records: {payload['row_count']}")

        if "date_range" in payload:
            dr = payload["date_range"]
            parts.append(f"Date Range: {dr.get('min', 'N/A')} to {dr.get('max', 'N/A')}")

        if "category_counts" in payload:
            parts.append("\nCategory Breakdown:")
            for category, counts in payload["category_counts"].items():
                parts.append(f"  {category}:")
                for value, count in counts.items():
                    parts.append(f"    - {value}: {count}")

        return "\n".join(parts)

    async def process(
        self,
        query: str,
        history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """Process query with analytics data included."""
        # Get document context
        chunks, sources = await self.retrieve_context(query)

        # Get analytics data
        analytics = await self.get_analytics_data()

        # Build prompts
        system_prompt = self.get_system_prompt()
        doc_context = self.build_context_prompt(chunks)
        analytics_context = self.build_analytics_context(analytics)

        # Combine context
        full_context = f"""DOCUMENT CONTEXT:
{doc_context}

ANALYTICS DATA:
{analytics_context}"""

        # Prepare messages
        messages = history or []
        messages.append({"role": "user", "content": query})

        # Generate response
        answer = await chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            context=full_context,
        )

        answer = self.post_process(answer)

        return AgentResponse(
            answer=answer,
            sources=sources,
            agent_name=self.name,
            metadata={
                "chunks_retrieved": len(chunks),
                "has_analytics": analytics is not None,
                "analytics_dataset": analytics.get("dataset_name") if analytics else None,
            },
        )
