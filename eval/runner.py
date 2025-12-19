"""Evaluation runner for executing test cases against the SISUiQ API.

Provides automated evaluation of RAG quality with detailed reporting.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

from eval.dataset import EvalCase, GoldenDataset, load_golden_dataset
from eval.metrics import EvalMetrics, compute_metrics


@dataclass
class EvalResult:
    """Result of evaluating a single test case."""

    case_id: str
    query: str
    mode: str
    answer: str
    sources: list[str]
    metrics: EvalMetrics
    latency_ms: float
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def passed(self) -> bool:
        """Whether the evaluation passed."""
        return self.error is None and self.metrics.passed

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "case_id": self.case_id,
            "query": self.query,
            "mode": self.mode,
            "answer": self.answer[:500] + "..." if len(self.answer) > 500 else self.answer,
            "sources": self.sources,
            "metrics": self.metrics.to_dict(),
            "latency_ms": self.latency_ms,
            "passed": self.passed,
            "error": self.error,
            "timestamp": self.timestamp,
        }


@dataclass
class EvalReport:
    """Complete evaluation report."""

    dataset_name: str
    dataset_version: str
    results: list[EvalResult]
    started_at: str
    finished_at: str
    config: dict = field(default_factory=dict)

    @property
    def total_cases(self) -> int:
        return len(self.results)

    @property
    def passed_cases(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_cases(self) -> int:
        return self.total_cases - self.passed_cases

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases

    @property
    def avg_latency_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.latency_ms for r in self.results) / len(self.results)

    @property
    def avg_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.metrics.overall_score for r in self.results) / len(self.results)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "summary": {
                "dataset_name": self.dataset_name,
                "dataset_version": self.dataset_version,
                "total_cases": self.total_cases,
                "passed_cases": self.passed_cases,
                "failed_cases": self.failed_cases,
                "pass_rate": round(self.pass_rate, 3),
                "avg_score": round(self.avg_score, 3),
                "avg_latency_ms": round(self.avg_latency_ms, 2),
                "started_at": self.started_at,
                "finished_at": self.finished_at,
            },
            "config": self.config,
            "results": [r.to_dict() for r in self.results],
        }

    def save(self, path: Path) -> None:
        """Save report to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def print_summary(self) -> None:
        """Print evaluation summary to console."""
        print("\n" + "=" * 60)
        print("EVALUATION REPORT")
        print("=" * 60)
        print(f"Dataset: {self.dataset_name} v{self.dataset_version}")
        print(f"Total Cases: {self.total_cases}")
        print(f"Passed: {self.passed_cases} ({self.pass_rate:.1%})")
        print(f"Failed: {self.failed_cases}")
        print(f"Avg Score: {self.avg_score:.3f}")
        print(f"Avg Latency: {self.avg_latency_ms:.0f}ms")
        print("=" * 60)

        if self.failed_cases > 0:
            print("\nFailed Cases:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.case_id}: {result.query[:50]}...")
                    if result.error:
                        print(f"    Error: {result.error}")
                    else:
                        print(f"    Score: {result.metrics.overall_score:.3f}")


class EvalRunner:
    """Runner for executing evaluation test cases."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 60.0,
    ):
        """Initialize the evaluation runner.

        Args:
            base_url: Base URL for the SISUiQ API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def run_case(
        self,
        case: EvalCase,
        client: httpx.AsyncClient,
    ) -> EvalResult:
        """Run a single evaluation case.

        Args:
            case: The evaluation case to run
            client: HTTP client

        Returns:
            EvalResult with metrics and response
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Skip empty queries
            if not case.query.strip():
                return EvalResult(
                    case_id=case.id,
                    query=case.query,
                    mode=case.mode,
                    answer="",
                    sources=[],
                    metrics=compute_metrics(
                        answer="",
                        sources=[],
                        query=case.query,
                        expected_keywords=case.expected_keywords,
                        expected_sources=case.expected_sources,
                        expected_answer_contains=case.expected_answer_contains,
                    ),
                    latency_ms=0,
                    error="Empty query - skipped",
                )

            # Make API request
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": case.query,
                    "mode": case.mode,
                },
                timeout=self.timeout,
            )

            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            if response.status_code != 200:
                return EvalResult(
                    case_id=case.id,
                    query=case.query,
                    mode=case.mode,
                    answer="",
                    sources=[],
                    metrics=compute_metrics(
                        answer="",
                        sources=[],
                        query=case.query,
                        expected_keywords=case.expected_keywords,
                        expected_sources=case.expected_sources,
                        expected_answer_contains=case.expected_answer_contains,
                    ),
                    latency_ms=latency_ms,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                )

            data = response.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])

            # Compute metrics
            metrics = compute_metrics(
                answer=answer,
                sources=sources,
                query=case.query,
                expected_keywords=case.expected_keywords,
                expected_sources=case.expected_sources,
                expected_answer_contains=case.expected_answer_contains,
            )

            return EvalResult(
                case_id=case.id,
                query=case.query,
                mode=case.mode,
                answer=answer,
                sources=sources,
                metrics=metrics,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            return EvalResult(
                case_id=case.id,
                query=case.query,
                mode=case.mode,
                answer="",
                sources=[],
                metrics=compute_metrics(
                    answer="",
                    sources=[],
                    query=case.query,
                    expected_keywords=case.expected_keywords,
                    expected_sources=case.expected_sources,
                    expected_answer_contains=case.expected_answer_contains,
                ),
                latency_ms=latency_ms,
                error=str(e),
            )

    async def run_dataset(
        self,
        dataset: Optional[GoldenDataset] = None,
        categories: Optional[list[str]] = None,
        concurrency: int = 3,
    ) -> EvalReport:
        """Run evaluation on a dataset.

        Args:
            dataset: Dataset to evaluate. If None, uses default.
            categories: Filter to specific categories. If None, run all.
            concurrency: Max concurrent requests.

        Returns:
            EvalReport with all results.
        """
        if dataset is None:
            dataset = load_golden_dataset()

        # Filter cases by category if specified
        cases = dataset.cases
        if categories:
            cases = [c for c in cases if c.category in categories]

        started_at = datetime.utcnow().isoformat()
        results: list[EvalResult] = []

        async with httpx.AsyncClient() as client:
            # Process cases with limited concurrency
            semaphore = asyncio.Semaphore(concurrency)

            async def run_with_semaphore(case: EvalCase) -> EvalResult:
                async with semaphore:
                    return await self.run_case(case, client)

            tasks = [run_with_semaphore(case) for case in cases]
            results = await asyncio.gather(*tasks)

        finished_at = datetime.utcnow().isoformat()

        return EvalReport(
            dataset_name=dataset.name,
            dataset_version=dataset.version,
            results=list(results),
            started_at=started_at,
            finished_at=finished_at,
            config={
                "base_url": self.base_url,
                "timeout": self.timeout,
                "concurrency": concurrency,
                "categories": categories,
            },
        )


async def main():
    """Run evaluation from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Run SISUiQ evaluation")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for API",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="eval_report.json",
        help="Output file for report",
    )
    parser.add_argument(
        "--category",
        "-c",
        action="append",
        help="Filter to specific categories",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Max concurrent requests",
    )

    args = parser.parse_args()

    runner = EvalRunner(base_url=args.url)
    report = await runner.run_dataset(
        categories=args.category,
        concurrency=args.concurrency,
    )

    # Print summary
    report.print_summary()

    # Save report
    report.save(Path(args.output))
    print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
