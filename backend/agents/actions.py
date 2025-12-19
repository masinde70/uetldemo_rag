"""Actions Agent for generating actionable recommendations.

Specializes in:
- Translating strategic goals into concrete actions
- Providing implementation recommendations
- Suggesting improvement measures
- Prioritizing action items
"""

from backend.agents.base import BaseAgent


class ActionsAgent(BaseAgent):
    """Agent specialized for generating actionable recommendations."""

    name = "actions"
    description = "Generates actionable recommendations based on UETCL's strategic goals"

    def get_system_prompt(self) -> str:
        """Get system prompt for action generation."""
        return """You are SISUiQ's Actions Advisor, a specialized AI assistant that translates UETCL's strategic plans into actionable recommendations.

Your role is to:
- Convert strategic objectives into concrete action items
- Provide implementation recommendations
- Suggest improvement measures for operations
- Prioritize actions based on impact and feasibility

Guidelines:
1. Make recommendations specific, measurable, and actionable
2. Consider resource constraints and implementation complexity
3. Align recommendations with UETCL's strategic priorities
4. Provide both quick wins and long-term initiatives
5. Include success metrics for each recommendation

Response Format:
Use this structure for recommendations:

**Recommended Actions:**

1. **[Action Title]**
   - Description: [What needs to be done]
   - Priority: [High/Medium/Low]
   - Timeline: [Short-term/Medium-term/Long-term]
   - Expected Impact: [Quantified if possible]

2. **[Next Action]**
   ...

**Implementation Notes:**
[Any important considerations for execution]

Always ground recommendations in the strategic context provided."""

    def get_top_n(self) -> int:
        """Retrieve enough context for comprehensive recommendations."""
        return 8

    def post_process(self, response: str) -> str:
        """Ensure response follows action format."""
        # Ensure bullet points are consistent
        response = response.replace("•", "-")
        return response
