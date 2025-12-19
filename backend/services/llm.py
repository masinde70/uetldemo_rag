"""OpenAI LLM service for chat completions.

This module provides the core LLM integration for SISUiQ, including
prompt building and chat completion functionality.

Note: Prompt templates have been moved to backend/prompts/ module.
This module re-exports the prompt builders for backward compatibility.
"""

import os
from typing import List, Optional

from openai import AsyncOpenAI

# Import from new prompts module for centralized prompt management
from backend.prompts import build_context
from backend.prompts import build_system_prompt as _build_system_prompt

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")


def build_system_prompt(mode: str, has_analytics: bool = False) -> str:
    """Build system prompt based on chat mode.

    This function wraps the centralized prompt builder for backward compatibility.
    For new code, consider using backend.prompts.build_system_prompt directly.

    Args:
        mode: Chat mode (strategy_qa, actions, analytics, regulatory)
        has_analytics: Whether analytics data is available

    Returns:
        System prompt string
    """
    return _build_system_prompt(mode=mode, has_analytics=has_analytics)


def build_context_prompt(
    chunks: list[dict],
    analytics_summary: Optional[dict] = None,
) -> str:
    """Build context section from retrieved chunks and analytics.

    This function wraps the centralized context builder for backward compatibility.
    For new code, consider using backend.prompts.build_context directly.

    Args:
        chunks: Retrieved document chunks
        analytics_summary: Optional analytics data summary

    Returns:
        Formatted context string
    """
    return build_context(chunks=chunks, analytics=analytics_summary)


async def chat_completion(
    messages: List[dict],
    system_prompt: str,
    context: str,
    temperature: float = 0.3,
) -> str:
    """
    Call OpenAI chat completion.

    Args:
        messages: Conversation history
        system_prompt: System prompt for the mode
        context: Retrieved context
        temperature: Model temperature

    Returns:
        Assistant response text
    """
    # Build full messages list
    full_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"CONTEXT:\n{context}"},
    ]

    # Add conversation history (limit to recent messages)
    for msg in messages[-10:]:  # Last 10 messages
        full_messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    response = await client.chat.completions.create(
        model=CHAT_MODEL,
        messages=full_messages,
        temperature=temperature,
        max_tokens=2000,
    )

    return response.choices[0].message.content or ""
