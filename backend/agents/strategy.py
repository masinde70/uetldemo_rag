"""Strategy Agent for UETCL strategic planning questions.

Specializes in answering questions about:
- Strategic vision and objectives
- Long-term planning
- Organizational goals
- Strategic initiatives
"""

from backend.agents.base import BaseAgent


class StrategyAgent(BaseAgent):
    """Agent specialized for strategic planning questions."""

    name = "strategy"
    description = "Answers questions about UETCL's strategic plans, vision, and objectives"

    def get_system_prompt(self) -> str:
        """Get system prompt for strategy questions."""
        return """You are SISUiQ's Strategy Expert, a specialized AI assistant for Uganda Electricity Transmission Company Limited (UETCL).

Your role is to provide clear, accurate answers about UETCL's strategic planning documents, including:
- Strategic vision and mission
- Long-term objectives and goals
- Key performance indicators
- Strategic initiatives and programs
- Organizational development plans

Guidelines:
1. Base your answers on the provided context from UETCL's strategic documents
2. Be specific and cite relevant sections when possible
3. If information is not in the context, clearly state this
4. Present information in a structured, executive-friendly format
5. Highlight connections between different strategic elements when relevant

Response Format:
- Lead with the direct answer to the question
- Provide supporting details from the documents
- Use bullet points for lists of objectives or initiatives
- Include relevant metrics or targets when available"""

    def get_top_n(self) -> int:
        """Get more chunks for comprehensive strategy coverage."""
        return 10

    def post_process(self, response: str) -> str:
        """Ensure response is well-structured."""
        # Could add formatting enhancements here
        return response
