"""Document lineage and citation tracking service.

Provides functionality for:
- Tracking which documents contributed to responses
- Citation formatting
- Source attribution
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Citation:
    """A single citation reference."""

    document_id: str
    document_name: str
    source_type: str  # uetcl, era
    page_number: Optional[int] = None
    section: Optional[str] = None
    relevance_score: float = 0.0
    chunk_id: Optional[str] = None

    def format_short(self) -> str:
        """Format as short citation (e.g., '[1] UETCL Strategic Plan, p.5')."""
        parts = [self.document_name]
        if self.page_number:
            parts.append(f"p.{self.page_number}")
        if self.section:
            parts.append(f"§{self.section}")
        return ", ".join(parts)

    def format_full(self) -> str:
        """Format as full citation with source type."""
        base = self.format_short()
        return f"[{self.source_type.upper()}] {base}"


@dataclass
class ResponseLineage:
    """Tracks the lineage of a response - which sources contributed."""

    response_id: str
    session_id: str
    query: str
    citations: list[Citation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_citation(self, citation: Citation) -> None:
        """Add a citation to this response."""
        self.citations.append(citation)

    def get_unique_documents(self) -> list[str]:
        """Get list of unique document IDs."""
        seen = set()
        result = []
        for c in self.citations:
            if c.document_id not in seen:
                result.append(c.document_id)
                seen.add(c.document_id)
        return result

    def format_citations_list(self) -> list[str]:
        """Format all citations as numbered list."""
        return [
            f"[{i+1}] {c.format_short()}"
            for i, c in enumerate(self.citations)
        ]


def extract_citations_from_chunks(chunks: list[dict]) -> list[Citation]:
    """Extract citation information from retrieved chunks.

    Args:
        chunks: Retrieved document chunks from RAG

    Returns:
        List of Citation objects
    """
    citations = []

    for chunk in chunks:
        # Extract metadata from chunk
        doc_id = chunk.get("document_id", chunk.get("id", "unknown"))
        doc_name = chunk.get("citation", chunk.get("source", "Unknown Document"))
        source_type = chunk.get("source_type", "uetcl")
        page = chunk.get("page_number", chunk.get("page"))
        section = chunk.get("section")
        score = chunk.get("score", chunk.get("relevance_score", 0.0))
        chunk_id = chunk.get("chunk_id", chunk.get("point_id"))

        citation = Citation(
            document_id=str(doc_id),
            document_name=doc_name,
            source_type=source_type,
            page_number=page if isinstance(page, int) else None,
            section=section,
            relevance_score=float(score) if score else 0.0,
            chunk_id=str(chunk_id) if chunk_id else None,
        )
        citations.append(citation)

    return citations


def format_inline_citations(text: str, citations: list[Citation]) -> str:
    """Add inline citation markers to response text.

    This is a simple implementation that adds citation numbers
    at the end of paragraphs. More sophisticated implementations
    could use NLP to determine citation placement.

    Args:
        text: Response text
        citations: List of citations to reference

    Returns:
        Text with citation markers
    """
    if not citations:
        return text

    # Simple approach: add citations at end
    citation_nums = ", ".join(f"[{i+1}]" for i in range(len(citations)))
    return f"{text}\n\nSources: {citation_nums}"


def create_response_lineage(
    response_id: str,
    session_id: str,
    query: str,
    chunks: list[dict],
) -> ResponseLineage:
    """Create a complete response lineage record.

    Args:
        response_id: ID of the generated response
        session_id: Chat session ID
        query: Original user query
        chunks: Retrieved document chunks

    Returns:
        ResponseLineage with all citation information
    """
    citations = extract_citations_from_chunks(chunks)

    return ResponseLineage(
        response_id=response_id,
        session_id=session_id,
        query=query,
        citations=citations,
    )
