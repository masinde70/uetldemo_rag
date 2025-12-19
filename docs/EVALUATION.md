# LLM Evaluation Framework

SISUiQ includes a comprehensive evaluation framework for testing RAG quality and tracking regression across model updates.

## Overview

The evaluation framework tests:
- **Keyword coverage**: Does the response contain expected keywords?
- **Source accuracy**: Are the right documents cited?
- **Answer containment**: Does the response include expected content?
- **Response quality**: Is the response well-formed and substantive?

## Quick Start

```bash
# Run evaluation with default golden dataset
make eval

# Or run directly with options
python -m eval.runner --url http://localhost:8000 --output eval_report.json
```

## Golden Dataset

The golden dataset (`eval/golden_dataset.json`) contains test cases organized by category:

| Category | Description |
|----------|-------------|
| `strategy` | UETCL strategic planning questions |
| `actions` | Action recommendation queries |
| `analytics` | Data analysis questions |
| `regulatory` | ERA compliance queries |
| `edge` | Edge cases and error handling |

### Test Case Structure

```json
{
  "id": "strat-001",
  "query": "What is UETCL's strategic vision?",
  "mode": "strategy_qa",
  "expected_keywords": ["transmission", "electricity", "grid"],
  "expected_sources": ["uetcl"],
  "expected_answer_contains": null,
  "min_relevance_score": 0.8,
  "category": "strategy",
  "notes": null
}
```

### Adding Test Cases

Edit `eval/golden_dataset.json` or use the Python API:

```python
from eval.dataset import EvalCase, load_golden_dataset, GoldenDataset

# Load existing dataset
dataset = load_golden_dataset()

# Add new case
new_case = EvalCase(
    id="custom-001",
    query="What is the transmission capacity target?",
    mode="strategy_qa",
    expected_keywords=["capacity", "MW", "target"],
    category="strategy",
)
dataset.cases.append(new_case)

# Save updated dataset
dataset.save(Path("eval/golden_dataset.json"))
```

## Metrics

### Keyword Coverage (30% weight)

Measures what percentage of expected keywords appear in the response.

```
Score = (keywords found) / (total expected keywords)
```

### Source Accuracy (20% weight)

Measures whether the expected source documents were cited.

```
Score = (matched sources) / (total expected sources)
```

### Answer Contains (30% weight)

Binary check if specific expected text appears in the response.

```
Score = 1.0 if contains expected text, else 0.0
```

### Response Quality (20% weight)

Evaluates response structure and substance:
- Minimum length (50+ characters)
- Not echoing the query
- No error indicators
- Contains substantive sentences

## Running Evaluations

### Command Line Options

```bash
python -m eval.runner \
  --url http://localhost:8000 \  # API base URL
  --output report.json \         # Output file
  --category strategy \          # Filter by category (can repeat)
  --category actions \
  --concurrency 3                # Parallel requests
```

### Python API

```python
import asyncio
from eval import EvalRunner, load_golden_dataset

async def run_eval():
    runner = EvalRunner(
        base_url="http://localhost:8000",
        timeout=60.0,
    )

    report = await runner.run_dataset(
        categories=["strategy", "actions"],
        concurrency=3,
    )

    # Print summary
    report.print_summary()

    # Save report
    report.save(Path("eval_report.json"))

    # Check pass rate
    if report.pass_rate < 0.8:
        raise Exception(f"Eval failed: {report.pass_rate:.1%} pass rate")

asyncio.run(run_eval())
```

## Report Format

The evaluation report includes:

```json
{
  "summary": {
    "dataset_name": "sisuiq-golden",
    "dataset_version": "1.0.0",
    "total_cases": 13,
    "passed_cases": 11,
    "failed_cases": 2,
    "pass_rate": 0.846,
    "avg_score": 0.782,
    "avg_latency_ms": 1250.5,
    "started_at": "2024-01-15T12:00:00Z",
    "finished_at": "2024-01-15T12:01:30Z"
  },
  "config": {
    "base_url": "http://localhost:8000",
    "timeout": 60.0,
    "concurrency": 3
  },
  "results": [
    {
      "case_id": "strat-001",
      "query": "What is UETCL's strategic vision?",
      "mode": "strategy_qa",
      "answer": "UETCL's strategic vision...",
      "sources": ["uetcl-strategic-plan.pdf"],
      "metrics": {
        "keyword_coverage": {"score": 0.75, "details": {...}},
        "source_accuracy": {"score": 1.0, "details": {...}},
        "answer_contains": {"score": 1.0, "details": {...}},
        "response_quality": {"score": 0.8, "details": {...}},
        "overall_score": 0.855,
        "passed": true
      },
      "latency_ms": 1150.5,
      "passed": true,
      "timestamp": "2024-01-15T12:00:05Z"
    }
  ]
}
```

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/ci.yml`:

```yaml
eval:
  runs-on: ubuntu-latest
  needs: [test-backend]  # Run after unit tests
  steps:
    - uses: actions/checkout@v4

    - name: Start services
      run: docker compose up -d

    - name: Wait for healthy
      run: |
        timeout 60 bash -c 'until curl -s http://localhost:8000/api/health; do sleep 2; done'

    - name: Run evaluation
      run: python -m eval.runner --output eval_report.json

    - name: Check pass rate
      run: |
        PASS_RATE=$(jq '.summary.pass_rate' eval_report.json)
        if (( $(echo "$PASS_RATE < 0.8" | bc -l) )); then
          echo "Evaluation failed: $PASS_RATE pass rate"
          exit 1
        fi

    - name: Upload report
      uses: actions/upload-artifact@v4
      with:
        name: eval-report
        path: eval_report.json
```

## Best Practices

### 1. Version Your Golden Dataset

Track changes to test cases:

```json
{
  "name": "sisuiq-golden",
  "version": "1.1.0",  // Bump on changes
  "description": "Added regulatory test cases"
}
```

### 2. Review Failed Cases

When cases fail, investigate:
- Is the expected answer still correct?
- Has the document corpus changed?
- Is there a model regression?

### 3. Balance Coverage

Aim for balanced category coverage:
- Strategy: 4-6 cases
- Actions: 3-4 cases
- Analytics: 2-3 cases
- Regulatory: 3-4 cases
- Edge cases: 2-3 cases

### 4. Set Appropriate Thresholds

Adjust `min_relevance_score` based on query difficulty:
- Straightforward queries: 0.8+
- Complex queries: 0.7
- Edge cases: 0.5

### 5. Monitor Trends

Track metrics over time:
- Pass rate should stay above 80%
- Average score should stay above 0.75
- Latency should stay below 3 seconds

## Extending the Framework

### Custom Metrics

Add new metrics in `eval/metrics.py`:

```python
def compute_custom_metric(answer: str, ...) -> MetricResult:
    # Your logic here
    return MetricResult(
        name="custom_metric",
        score=0.85,
        details={"custom": "data"},
    )
```

### Custom Test Cases

Implement category-specific validation:

```python
class RegulatoryEvalCase(EvalCase):
    """Extended case with regulatory-specific fields."""
    era_section: Optional[str] = None
    compliance_type: Optional[str] = None
```

## Troubleshooting

### All Cases Failing

1. Check backend is running: `curl http://localhost:8000/api/health`
2. Verify documents are ingested: Check Qdrant collection
3. Check OpenAI API key is valid

### Slow Evaluations

1. Reduce concurrency if rate-limited
2. Check network latency to OpenAI
3. Verify Qdrant performance

### Inconsistent Results

1. Set `temperature=0` in LLM calls for determinism
2. Use fixed random seed if applicable
3. Check for document updates that change context
