# Multi-Agent Architecture

SISUiQ uses a multi-agent architecture where specialized agents handle different types of queries. Each agent has domain-specific prompts, retrieval strategies, and response formatting.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentOrchestrator                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   route_to_agent()                   │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Strategy   │ │   Actions   │ │  Analytics  │          │
│  │   Agent     │ │    Agent    │ │    Agent    │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         │               │               │                  │
│         └───────────────┼───────────────┘                  │
│                         ▼                                   │
│              ┌──────────────────┐                          │
│              │    BaseAgent     │                          │
│              │ - retrieve_context                          │
│              │ - build_prompt                              │
│              │ - process                                   │
│              └──────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Available Agents

| Agent | Mode | Description |
|-------|------|-------------|
| StrategyAgent | `strategy_qa` | UETCL strategic planning questions |
| ActionsAgent | `actions` | Actionable recommendations |
| AnalyticsAgent | `analytics` | Operational data analysis |
| RegulatoryAgent | `regulatory` | ERA compliance questions |

## Usage

### Basic Usage

```python
from backend.agents import route_to_agent

# Simple routing
response = await route_to_agent(
    query="What is UETCL's strategic vision?",
    mode="strategy_qa",
    db=db_session,
    history=[],
)

print(response.answer)
print(response.sources)
print(response.agent_name)  # "strategy"
```

### Using the Orchestrator

```python
from backend.agents import AgentOrchestrator

orchestrator = AgentOrchestrator(db_session)

# Single agent query
response = await orchestrator.process(
    query="What actions reduce transmission losses?",
    mode="actions",
)

# Multi-agent query (query multiple agents)
responses = await orchestrator.multi_agent_query(
    query="How can we improve grid reliability?",
    modes=["strategy_qa", "actions", "analytics"],
)

# Synthesize multiple responses
synthesis = await orchestrator.synthesize_responses(responses, query)
```

### Direct Agent Usage

```python
from backend.agents import StrategyAgent

agent = StrategyAgent(db_session)
response = await agent.process(
    query="What are the key strategic objectives?",
    history=[],
)
```

## Agent Response

All agents return an `AgentResponse`:

```python
@dataclass
class AgentResponse:
    answer: str              # The generated response
    sources: list[str]       # Source citations
    agent_name: str          # Which agent handled it
    confidence: float        # Confidence score (0-1)
    metadata: dict           # Additional info
```

## Creating Custom Agents

### 1. Extend BaseAgent

```python
from backend.agents.base import BaseAgent, AgentResponse

class CustomAgent(BaseAgent):
    name = "custom"
    description = "Handles custom domain queries"

    def get_system_prompt(self) -> str:
        return """You are a custom domain expert..."""

    def get_retrieval_filters(self) -> Optional[dict]:
        # Filter documents by source
        return {"source": "custom_docs"}

    def get_top_n(self) -> int:
        # Number of chunks to retrieve
        return 5

    def post_process(self, response: str) -> str:
        # Custom response formatting
        return response
```

### 2. Register with Orchestrator

```python
# In backend/agents/orchestrator.py
MODE_AGENT_MAP["custom"] = CustomAgent
```

### 3. Add to Chat Modes (Optional)

```python
# In backend/models.py
class ChatMode(str, Enum):
    STRATEGY_QA = "strategy_qa"
    ACTIONS = "actions"
    ANALYTICS = "analytics"
    REGULATORY = "regulatory"
    CUSTOM = "custom"  # New mode
```

## Agent Specializations

### StrategyAgent

**Prompt Focus:**
- Strategic vision and mission
- Long-term objectives
- KPIs and targets
- Strategic initiatives

**Response Format:**
- Direct answer first
- Supporting details
- Bullet points for lists
- Metrics when available

### ActionsAgent

**Prompt Focus:**
- Actionable recommendations
- Implementation guidance
- Prioritization
- Success metrics

**Response Format:**
```markdown
**Recommended Actions:**

1. **[Action Title]**
   - Description: [What]
   - Priority: [High/Medium/Low]
   - Timeline: [When]
   - Expected Impact: [Outcome]
```

### AnalyticsAgent

**Prompt Focus:**
- Data analysis and trends
- Performance metrics
- Strategic alignment
- Data-driven recommendations

**Special Features:**
- Loads analytics snapshots from database
- Combines document context with operational data

**Response Format:**
```markdown
**Data Summary:**
[Key metrics]

**Trend Analysis:**
[Patterns and trends]

**Strategic Alignment:**
[Comparison to targets]

**Recommendations:**
[Data-driven suggestions]
```

### RegulatoryAgent

**Prompt Focus:**
- ERA requirements
- Grid code provisions
- License conditions
- Compliance guidance

**Response Format:**
```markdown
**Regulatory Requirement:**
[The requirement]

**Source:**
[Document and section]

**Key Points:**
- [Obligations]
- [Deadlines]
- [Penalties]

**Compliance Guidance:**
[How to comply]
```

**Post-Processing:**
- Adds disclaimer about consulting official documents

## Best Practices

### 1. Prompt Engineering

Each agent's system prompt should:
- Clearly define the agent's role
- List specific topics it handles
- Provide response formatting guidelines
- Include domain-specific terminology

### 2. Retrieval Tuning

Adjust `get_top_n()` based on:
- Query complexity typical for the domain
- Document density in the corpus
- Response detail requirements

### 3. Source Filtering

Use `get_retrieval_filters()` to:
- Prioritize relevant document types
- Exclude unrelated sources
- Improve response relevance

### 4. Response Post-Processing

Use `post_process()` for:
- Adding disclaimers (regulatory)
- Formatting standardization
- Citation formatting
- Quality checks

## Testing Agents

```python
import pytest
from backend.agents import StrategyAgent

@pytest.mark.asyncio
async def test_strategy_agent(db_session):
    agent = StrategyAgent(db_session)

    response = await agent.process(
        query="What is UETCL's vision?",
        history=[],
    )

    assert response.agent_name == "strategy"
    assert len(response.answer) > 100
    assert "vision" in response.answer.lower() or len(response.sources) > 0
```

## Monitoring

Track agent performance:

```python
# Log agent metrics
logger.info(
    "Agent response",
    extra={
        "agent": response.agent_name,
        "confidence": response.confidence,
        "chunks_retrieved": response.metadata["chunks_retrieved"],
        "latency_ms": latency,
    }
)
```

## Future Extensions

Planned enhancements:
- **Agent Selection AI**: Automatic mode detection from query
- **Agent Chaining**: Multi-step reasoning across agents
- **Memory**: Agent-specific conversation context
- **Tools**: External tool integration per agent
