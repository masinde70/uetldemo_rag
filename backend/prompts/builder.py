"""Prompt builder utilities for SISUiQ.

This module provides functions to build system prompts and context strings
from templates and dynamic data.
"""

from typing import Any

from backend.prompts.templates import (
    AGENT_TEMPLATES,
    ANALYTICS_AVAILABLE_TEMPLATE,
    ANALYTICS_HEADER,
    BASE_PERSONA,
    CITATION_FORMAT_GUIDANCE,
    CONTEXT_HEADER,
    MODE_TEMPLATES,
)


def build_system_prompt(
    mode: str,
    has_analytics: bool = False,
    agent_type: str | None = None,
    custom_instructions: str | None = None,
    include_citation_guidance: bool = True,
) -> str:
    """Build a complete system prompt from templates.

    Args:
        mode: Chat mode (strategy_qa, actions, analytics, regulatory)
        has_analytics: Whether analytics data is available
        agent_type: Optional agent type for agent-specific prompts
        custom_instructions: Optional additional instructions
        include_citation_guidance: Whether to include citation format guidance

    Returns:
        Complete system prompt string
    """
    parts: list[str] = []

    # Add base persona
    parts.append(BASE_PERSONA.strip())

    # Add agent-specific prompt if specified
    if agent_type and agent_type in AGENT_TEMPLATES:
        agent_prompt = AGENT_TEMPLATES[agent_type]["system_prompt"]
        parts.append(f"\n{agent_prompt.strip()}")

    # Add mode-specific template
    if mode in MODE_TEMPLATES:
        parts.append(MODE_TEMPLATES[mode].strip())
    else:
        # Default to strategy_qa if mode not found
        parts.append(MODE_TEMPLATES["strategy_qa"].strip())

    # Add analytics availability note
    if has_analytics:
        parts.append(ANALYTICS_AVAILABLE_TEMPLATE.strip())

    # Add citation guidance
    if include_citation_guidance:
        parts.append(CITATION_FORMAT_GUIDANCE.strip())

    # Add custom instructions
    if custom_instructions:
        parts.append(f"\nADDITIONAL INSTRUCTIONS:\n{custom_instructions.strip()}")

    return "\n\n".join(parts)


def build_context(
    chunks: list[dict[str, Any]],
    analytics: dict[str, Any] | None = None,
    max_chunks: int = 10,
) -> str:
    """Build context section from retrieved chunks and analytics.

    Args:
        chunks: List of retrieved document chunks with text and metadata
        analytics: Optional analytics data summary
        max_chunks: Maximum number of chunks to include

    Returns:
        Formatted context string
    """
    context_parts: list[str] = []

    # Add document chunks
    if chunks:
        context_parts.append(CONTEXT_HEADER)

        for i, chunk in enumerate(chunks[:max_chunks], 1):
            citation = _format_citation(chunk)
            text = chunk.get("text", "").strip()
            context_parts.append(f"\n[{i}] {citation}\n{text}")

    # Add analytics summary
    if analytics:
        context_parts.append(f"\n\n{ANALYTICS_HEADER}")
        context_parts.append(_format_analytics_summary(analytics))

    return "\n".join(context_parts) if context_parts else "No context available."


def _format_citation(chunk: dict[str, Any]) -> str:
    """Format a chunk's citation string.

    Args:
        chunk: Document chunk with metadata

    Returns:
        Formatted citation string
    """
    # Try to get citation from various possible fields
    citation = chunk.get("citation")

    if not citation:
        source = chunk.get("source", chunk.get("title", "Unknown Source"))
        page = chunk.get("page")

        if page:
            citation = f"[{source} p.{page}]"
        else:
            citation = f"[{source}]"

    return citation


def _format_analytics_summary(summary: dict[str, Any]) -> str:
    """Format analytics summary for the prompt.

    Args:
        summary: Analytics data summary

    Returns:
        Formatted analytics string
    """
    parts: list[str] = []

    # Dataset name
    if "dataset_name" in summary:
        parts.append(f"Dataset: {summary['dataset_name']}")

    # Get payload (might be nested or at top level)
    payload = summary.get("payload", summary)

    # SAIDI/SAIFI metrics
    if "saidi" in payload:
        parts.append(
            f"SAIDI (System Average Interruption Duration Index): {payload['saidi']}"
        )
    if "saifi" in payload:
        parts.append(
            f"SAIFI (System Average Interruption Frequency Index): {payload['saifi']}"
        )

    # Event counts
    if "total_events" in payload:
        parts.append(f"Total Outage Events: {payload['total_events']}")
    if "total_customers_affected" in payload:
        parts.append(
            f"Total Customers Affected: {payload['total_customers_affected']:,}"
        )

    # Regional breakdown
    if "top_regions" in payload:
        parts.append("\nRegional Breakdown:")
        for region in payload["top_regions"][:5]:
            parts.append(
                f"  - {region['region']}: {region['events']} events "
                f"({region['percentage']}%)"
            )

    # Outage causes
    if "outage_causes" in payload:
        parts.append("\nOutage Causes:")
        for cause, pct in payload["outage_causes"].items():
            cause_name = cause.replace("_", " ").title()
            parts.append(f"  - {cause_name}: {pct}%")

    # Monthly trend
    if "monthly_trend" in payload:
        parts.append("\nMonthly Trend:")
        for month in payload["monthly_trend"][:6]:
            parts.append(f"  - {month['month']}: {month['events']} events")

    # Generic row count
    if "row_count" in payload:
        parts.append(f"Records: {payload['row_count']}")

    # Date range
    if "date_range" in payload:
        dr = payload["date_range"]
        parts.append(f"Date Range: {dr.get('min', 'N/A')} to {dr.get('max', 'N/A')}")

    # Category counts
    if "category_counts" in payload:
        parts.append("\nCategory Breakdown:")
        for col, counts in payload["category_counts"].items():
            parts.append(f"  {col}:")
            for cat, count in list(counts.items())[:5]:
                parts.append(f"    - {cat}: {count}")

    # Numeric summary
    if "numeric_summary" in payload:
        parts.append("\nNumeric Metrics:")
        for col, stats in payload["numeric_summary"].items():
            mean = stats.get("mean")
            if mean is not None:
                parts.append(
                    f"  {col}: avg={mean:.2f}, "
                    f"min={stats.get('min')}, max={stats.get('max')}"
                )

    # Notes
    if "note" in payload:
        parts.append(f"\nNote: {payload['note']}")

    return "\n".join(parts) if parts else "No analytics data available."


def get_agent_info(agent_type: str) -> dict[str, str] | None:
    """Get agent information by type.

    Args:
        agent_type: Agent type key

    Returns:
        Agent info dict with name, description, system_prompt or None
    """
    return AGENT_TEMPLATES.get(agent_type)


def list_available_modes() -> list[str]:
    """List all available chat modes.

    Returns:
        List of mode names
    """
    return list(MODE_TEMPLATES.keys())


def list_available_agents() -> list[dict[str, str]]:
    """List all available agent types.

    Returns:
        List of agent info dicts
    """
    return [
        {"type": key, "name": info["name"], "description": info["description"]}
        for key, info in AGENT_TEMPLATES.items()
    ]
