# SISUiQ Prompting Guide

This document describes the system prompt architecture and how to customize prompts for different use cases.

## Overview

SISUiQ uses a modular prompt system located in `backend/prompts/`:

```
backend/prompts/
├── __init__.py      # Exports
├── templates.py     # Prompt templates
└── builder.py       # Prompt construction functions
```

## Prompt Structure

Every prompt consists of:

1. **Base Persona** - Core identity and rules
2. **Mode Template** - Mode-specific focus and guidance
3. **Analytics Note** - (Optional) When analytics data is available
4. **Citation Guidance** - How to format citations
5. **Custom Instructions** - (Optional) Additional context

## Available Modes

| Mode | Focus | Use Case |
|------|-------|----------|
| `strategy_qa` | UETCL strategic plans | Q&A about strategy docs |
| `actions` | Actionable recommendations | Converting insights to tasks |
| `analytics` | Data + strategy combined | Performance analysis |
| `regulatory` | ERA regulations | Compliance guidance |

## Usage

### Basic Usage

```python
from backend.prompts import build_system_prompt, build_context

# Build system prompt for strategy mode
system_prompt = build_system_prompt(
    mode="strategy_qa",
    has_analytics=False,
)

# Build context from retrieved chunks
context = build_context(
    chunks=[
        {"text": "...", "source": "UETCL Strategic Plan", "page": 12},
        {"text": "...", "source": "UETCL Strategic Plan", "page": 15},
    ],
    analytics=None,
)
```

### With Analytics Data

```python
system_prompt = build_system_prompt(
    mode="analytics",
    has_analytics=True,
)

context = build_context(
    chunks=retrieved_chunks,
    analytics={
        "dataset_name": "Outages 2024",
        "payload": {
            "saidi": 45.2,
            "saifi": 12.3,
            "total_events": 1250,
            "top_regions": [
                {"region": "Central", "events": 450, "percentage": 36},
            ],
        },
    },
)
```

### With Custom Instructions

```python
system_prompt = build_system_prompt(
    mode="regulatory",
    custom_instructions="Focus specifically on transmission license requirements.",
)
```

## Prompt Templates

### Base Persona

The base persona establishes:

- Identity as SISUiQ assistant
- Professional, consultative tone
- Critical rules:
  - Only use provided context
  - Always cite sources
  - State when context is insufficient
  - Never fabricate information

### Mode Templates

Each mode adds specific focus areas and guidance:

**Strategy Q&A:**
- Strategic objectives and KPIs
- Implementation roadmaps
- Resource allocation

**Actions:**
- Numbered action items
- Owners and timelines
- Priority and feasibility

**Analytics:**
- Reliability metrics
- Trend analysis
- Data-driven recommendations

**Regulatory:**
- Specific clause citations
- Compliance requirements
- Penalty frameworks

## Citation Format

SISUiQ uses consistent citation formatting:

```
Single page:    [Source Name p.12]
Page range:     [Source Name pp.12-15]
General:        [Source Name]
Multiple:       [Source A p.5] [Source B p.23]
```

Citations should appear immediately after relevant statements.

## Customization

### Adding a New Mode

1. Add template to `templates.py`:

```python
MODE_TEMPLATES = {
    # ... existing modes ...
    "new_mode": """
MODE: New Mode Name
Description of what this mode focuses on.

FOCUS AREAS:
- Area 1
- Area 2

GUIDANCE:
- How to handle queries
- What to prioritize
""",
}
```

2. Update `ChatMode` enum in `backend/models.py`:

```python
class ChatMode(str, enum.Enum):
    # ... existing modes ...
    NEW_MODE = "new_mode"
```

### Adding Agent Templates

For multi-agent architecture:

```python
AGENT_TEMPLATES = {
    "new_agent": {
        "name": "Agent Display Name",
        "description": "What this agent specializes in",
        "system_prompt": """Detailed system prompt for this agent...""",
    },
}
```

## Best Practices

### Prompt Design

1. **Be specific** - Vague instructions lead to vague outputs
2. **Include examples** - Show expected formats in the prompt
3. **Set boundaries** - Clearly state what NOT to do
4. **Test variations** - A/B test prompt changes

### Context Management

1. **Limit chunk count** - Too much context dilutes relevance
2. **Order by relevance** - Best matches first
3. **Include metadata** - Page numbers enable precise citations
4. **Format consistently** - Numbered chunks help tracking

### Handling Edge Cases

The prompts include guidance for:

- **Insufficient context**: Explain what's missing, suggest sources
- **Conflicting information**: Cite both sources, note discrepancy
- **Outdated data**: Note dates when available
- **Speculation requests**: Decline and explain limitations

## Testing

```python
# Test prompt building
from backend.prompts import build_system_prompt, list_available_modes

# List all modes
modes = list_available_modes()
print(modes)  # ['strategy_qa', 'actions', 'analytics', 'regulatory']

# Test each mode
for mode in modes:
    prompt = build_system_prompt(mode=mode)
    assert "SISUiQ" in prompt
    assert "citation" in prompt.lower()
```

## Related Documentation

- [Architecture](architecture/README.md) - System design
- [API Documentation](api/README.md) - Chat endpoint usage
- [EVALUATION.md](EVALUATION.md) - Testing prompt quality
