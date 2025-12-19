"""Streaming LLM service for real-time token-by-token responses.

This module provides async generators for streaming chat completions
from OpenAI, enabling real-time token streaming to the frontend.
"""

import os
from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI

from backend.prompts import build_context, build_system_prompt

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")


async def stream_chat_completion(
    messages: list[dict],
    system_prompt: str,
    context: str,
    temperature: float = 0.3,
) -> AsyncGenerator[str, None]:
    """Stream chat completion tokens from OpenAI.

    This async generator yields tokens as they are received from the API,
    enabling real-time streaming to the frontend.

    Args:
        messages: Conversation history
        system_prompt: System prompt for the mode
        context: Retrieved RAG context
        temperature: Model temperature (default 0.3)

    Yields:
        String tokens as they are received from OpenAI
    """
    # Build full messages list
    full_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"CONTEXT:\n{context}"},
    ]

    # Add conversation history (limit to recent messages)
    for msg in messages[-10:]:
        full_messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    # Create streaming completion
    stream = await client.chat.completions.create(
        model=CHAT_MODEL,
        messages=full_messages,
        temperature=temperature,
        max_tokens=2000,
        stream=True,
    )

    # Yield tokens as they arrive
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def stream_with_metadata(
    messages: list[dict],
    mode: str,
    context_chunks: list[dict],
    analytics_data: Optional[dict] = None,
    temperature: float = 0.3,
) -> AsyncGenerator[dict, None]:
    """Stream chat completion with metadata events.

    Yields structured events including:
    - start: Initial metadata (session info)
    - token: Individual tokens
    - sources: Source citations
    - done: Completion signal with full response

    Args:
        messages: Conversation history
        mode: Chat mode (strategy_qa, actions, analytics, regulatory)
        context_chunks: Retrieved document chunks
        analytics_data: Optional analytics data for analytics mode
        temperature: Model temperature

    Yields:
        Dict events with type and data fields
    """
    # Build prompts
    has_analytics = analytics_data is not None
    system_prompt = build_system_prompt(mode=mode, has_analytics=has_analytics)
    context = build_context(chunks=context_chunks, analytics=analytics_data)

    # Extract sources for citation
    sources = []
    seen = set()
    for chunk in context_chunks:
        citation = chunk.get("citation", chunk.get("source", ""))
        if citation and citation not in seen:
            sources.append(citation)
            seen.add(citation)

    # Yield start event
    yield {"type": "start", "data": {"sources": sources}}

    # Collect full response for final event
    full_response = ""

    # Stream tokens
    async for token in stream_chat_completion(
        messages=messages,
        system_prompt=system_prompt,
        context=context,
        temperature=temperature,
    ):
        full_response += token
        yield {"type": "token", "data": {"content": token}}

    # Yield done event with full response
    yield {
        "type": "done",
        "data": {
            "content": full_response,
            "sources": sources,
            "analytics": analytics_data.get("payload") if analytics_data else None,
        },
    }
