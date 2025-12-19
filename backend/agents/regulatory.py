"""Regulatory Agent for ERA compliance questions.

Specializes in:
- ERA (Electricity Regulatory Authority) requirements
- Grid code compliance
- License conditions
- Reporting obligations
"""

from typing import Optional

from backend.agents.base import BaseAgent
from backend.models import DocumentSource


class RegulatoryAgent(BaseAgent):
    """Agent specialized for regulatory compliance questions."""

    name = "regulatory"
    description = "Answers questions about ERA regulations and compliance requirements"

    def get_system_prompt(self) -> str:
        """Get system prompt for regulatory questions."""
        return """You are SISUiQ's Regulatory Expert, a specialized AI assistant for ERA (Electricity Regulatory Authority of Uganda) compliance matters.

Your role is to:
- Explain ERA regulatory requirements
- Clarify grid code provisions
- Answer questions about license conditions
- Guide on reporting obligations
- Provide compliance recommendations

Guidelines:
1. Base answers strictly on official ERA documents
2. Quote relevant sections when possible
3. Clearly distinguish between mandatory requirements and guidance
4. Highlight compliance deadlines and penalties when mentioned
5. If unsure, recommend consulting the official ERA documentation

Response Format:
Structure regulatory answers as:

**Regulatory Requirement:**
[The specific requirement or provision]

**Source:**
[Document name and section if available]

**Key Points:**
- [Specific obligations]
- [Deadlines or timelines]
- [Penalties for non-compliance if mentioned]

**Compliance Guidance:**
[Recommendations for meeting the requirement]

Always emphasize that official ERA documents should be consulted for binding requirements."""

    def get_retrieval_filters(self) -> Optional[dict]:
        """Prioritize ERA documents for regulatory questions."""
        # Note: Filter might need adjustment based on how source is stored
        # return {"source": DocumentSource.ERA.value}
        return None  # Disabled until source filtering is fixed

    def get_top_n(self) -> int:
        """Get enough context for comprehensive regulatory answers."""
        return 10

    def post_process(self, response: str) -> str:
        """Add regulatory disclaimer if not present."""
        disclaimer = "\n\n*Note: This information is for guidance only. Please refer to official ERA documentation for authoritative requirements.*"

        if "official" not in response.lower() and "consult" not in response.lower():
            response = response + disclaimer

        return response
