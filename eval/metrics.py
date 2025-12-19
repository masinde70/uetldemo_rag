"""Evaluation metrics for RAG quality assessment.

Provides metrics for measuring:
- Answer relevance
- Source citation accuracy
- Keyword coverage
- Response quality
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricResult:
    """Result of a single metric computation."""

    name: str
    score: float  # 0.0 to 1.0
    details: Optional[dict] = None

    @property
    def passed(self) -> bool:
        """Whether the metric passes (score >= 0.5)."""
        return self.score >= 0.5


@dataclass
class EvalMetrics:
    """Collection of all evaluation metrics for a response."""

    keyword_coverage: MetricResult
    source_accuracy: MetricResult
    answer_contains: MetricResult
    response_quality: MetricResult

    @property
    def overall_score(self) -> float:
        """Weighted average of all metrics."""
        weights = {
            "keyword_coverage": 0.3,
            "source_accuracy": 0.2,
            "answer_contains": 0.3,
            "response_quality": 0.2,
        }
        total = (
            self.keyword_coverage.score * weights["keyword_coverage"]
            + self.source_accuracy.score * weights["source_accuracy"]
            + self.answer_contains.score * weights["answer_contains"]
            + self.response_quality.score * weights["response_quality"]
        )
        return round(total, 3)

    @property
    def passed(self) -> bool:
        """Whether overall evaluation passes."""
        return self.overall_score >= 0.6

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "keyword_coverage": {
                "score": self.keyword_coverage.score,
                "details": self.keyword_coverage.details,
            },
            "source_accuracy": {
                "score": self.source_accuracy.score,
                "details": self.source_accuracy.details,
            },
            "answer_contains": {
                "score": self.answer_contains.score,
                "details": self.answer_contains.details,
            },
            "response_quality": {
                "score": self.response_quality.score,
                "details": self.response_quality.details,
            },
            "overall_score": self.overall_score,
            "passed": self.passed,
        }


def compute_keyword_coverage(
    answer: str,
    expected_keywords: list[str],
) -> MetricResult:
    """Compute keyword coverage in the answer.

    Args:
        answer: The LLM response
        expected_keywords: Keywords expected in the answer

    Returns:
        MetricResult with coverage score
    """
    if not expected_keywords:
        return MetricResult(
            name="keyword_coverage",
            score=1.0,
            details={"message": "No keywords expected"},
        )

    answer_lower = answer.lower()
    found = []
    missing = []

    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            found.append(keyword)
        else:
            missing.append(keyword)

    score = len(found) / len(expected_keywords) if expected_keywords else 1.0

    return MetricResult(
        name="keyword_coverage",
        score=round(score, 3),
        details={
            "found": found,
            "missing": missing,
            "total_expected": len(expected_keywords),
        },
    )


def compute_source_accuracy(
    sources: list[str],
    expected_sources: list[str],
) -> MetricResult:
    """Compute source citation accuracy.

    Args:
        sources: Sources returned by the system
        expected_sources: Expected source patterns

    Returns:
        MetricResult with accuracy score
    """
    if not expected_sources:
        return MetricResult(
            name="source_accuracy",
            score=1.0,
            details={"message": "No specific sources expected"},
        )

    matched = []
    unmatched = []

    for expected in expected_sources:
        pattern = expected.lower()
        found = False
        for source in sources:
            if pattern in source.lower():
                matched.append(expected)
                found = True
                break
        if not found:
            unmatched.append(expected)

    score = len(matched) / len(expected_sources) if expected_sources else 1.0

    return MetricResult(
        name="source_accuracy",
        score=round(score, 3),
        details={
            "matched": matched,
            "unmatched": unmatched,
            "sources_returned": len(sources),
        },
    )


def compute_answer_contains(
    answer: str,
    expected_content: Optional[str],
) -> MetricResult:
    """Check if answer contains expected content.

    Args:
        answer: The LLM response
        expected_content: Text that should appear in answer

    Returns:
        MetricResult with containment check
    """
    if not expected_content:
        return MetricResult(
            name="answer_contains",
            score=1.0,
            details={"message": "No specific content expected"},
        )

    contains = expected_content.lower() in answer.lower()

    return MetricResult(
        name="answer_contains",
        score=1.0 if contains else 0.0,
        details={
            "expected": expected_content,
            "found": contains,
        },
    )


def compute_response_quality(
    answer: str,
    query: str,
) -> MetricResult:
    """Compute basic response quality metrics.

    Checks for:
    - Minimum length
    - Not just echoing the query
    - Contains substantive content

    Args:
        answer: The LLM response
        query: Original query

    Returns:
        MetricResult with quality score
    """
    issues = []
    score = 1.0

    # Check minimum length
    if len(answer) < 50:
        issues.append("Response too short")
        score -= 0.3

    # Check if just echoing query
    if query.lower() in answer.lower() and len(answer) < len(query) * 2:
        issues.append("Response may just echo query")
        score -= 0.2

    # Check for error indicators
    error_patterns = [
        r"i don't have",
        r"i cannot",
        r"i'm not able",
        r"no information",
        r"error occurred",
    ]
    for pattern in error_patterns:
        if re.search(pattern, answer.lower()):
            issues.append(f"Contains error indicator: {pattern}")
            score -= 0.2
            break

    # Check for substantive content (sentences)
    sentences = re.split(r"[.!?]+", answer)
    substantive_sentences = [s for s in sentences if len(s.strip()) > 20]
    if len(substantive_sentences) < 2:
        issues.append("Lacks substantive content")
        score -= 0.2

    score = max(0.0, min(1.0, score))

    return MetricResult(
        name="response_quality",
        score=round(score, 3),
        details={
            "issues": issues,
            "answer_length": len(answer),
            "sentence_count": len(substantive_sentences),
        },
    )


def compute_metrics(
    answer: str,
    sources: list[str],
    query: str,
    expected_keywords: list[str],
    expected_sources: list[str],
    expected_answer_contains: Optional[str] = None,
) -> EvalMetrics:
    """Compute all evaluation metrics for a response.

    Args:
        answer: The LLM response
        sources: Sources returned by the system
        query: Original query
        expected_keywords: Keywords expected in answer
        expected_sources: Expected source patterns
        expected_answer_contains: Text that should appear in answer

    Returns:
        EvalMetrics with all computed metrics
    """
    return EvalMetrics(
        keyword_coverage=compute_keyword_coverage(answer, expected_keywords),
        source_accuracy=compute_source_accuracy(sources, expected_sources),
        answer_contains=compute_answer_contains(answer, expected_answer_contains),
        response_quality=compute_response_quality(answer, query),
    )
