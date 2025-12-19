"""Golden dataset management for evaluation.

Handles loading, saving, and managing evaluation test cases
with expected outputs for regression testing.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class EvalCase:
    """A single evaluation test case."""

    id: str
    query: str
    mode: str  # strategy_qa, actions, analytics, regulatory
    expected_keywords: list[str] = field(default_factory=list)
    expected_sources: list[str] = field(default_factory=list)
    expected_answer_contains: Optional[str] = None
    min_relevance_score: float = 0.7
    category: str = "general"
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EvalCase":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class GoldenDataset:
    """Collection of evaluation test cases."""

    name: str
    version: str
    cases: list[EvalCase]
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "cases": [c.to_dict() for c in self.cases],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GoldenDataset":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            cases=[EvalCase.from_dict(c) for c in data["cases"]],
        )

    def save(self, path: Path) -> None:
        """Save dataset to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "GoldenDataset":
        """Load dataset from JSON file."""
        with open(path) as f:
            return cls.from_dict(json.load(f))


def load_golden_dataset(path: Optional[Path] = None) -> GoldenDataset:
    """Load the golden dataset for evaluation.

    Args:
        path: Path to dataset JSON. If None, uses default.

    Returns:
        GoldenDataset with test cases.
    """
    if path is None:
        path = Path(__file__).parent / "golden_dataset.json"

    if not path.exists():
        # Return default dataset if file doesn't exist
        return get_default_dataset()

    return GoldenDataset.load(path)


def get_default_dataset() -> GoldenDataset:
    """Get the default golden dataset with UETCL-specific test cases."""
    return GoldenDataset(
        name="sisuiq-golden",
        version="1.0.0",
        description="Golden dataset for SISUiQ RAG evaluation",
        cases=[
            # Strategy Q&A cases
            EvalCase(
                id="strat-001",
                query="What is UETCL's strategic vision?",
                mode="strategy_qa",
                expected_keywords=["transmission", "electricity", "uganda", "grid"],
                category="strategy",
                min_relevance_score=0.8,
            ),
            EvalCase(
                id="strat-002",
                query="What are UETCL's key strategic objectives?",
                mode="strategy_qa",
                expected_keywords=["objective", "goal", "target"],
                category="strategy",
            ),
            EvalCase(
                id="strat-003",
                query="How does UETCL plan to expand transmission capacity?",
                mode="strategy_qa",
                expected_keywords=["expansion", "capacity", "infrastructure"],
                category="strategy",
            ),
            # Actions cases
            EvalCase(
                id="act-001",
                query="What actions should we take to reduce transmission losses?",
                mode="actions",
                expected_keywords=["reduce", "loss", "action", "implement"],
                category="actions",
            ),
            EvalCase(
                id="act-002",
                query="How can we improve grid reliability?",
                mode="actions",
                expected_keywords=["reliability", "improve", "maintenance"],
                category="actions",
            ),
            # Analytics cases
            EvalCase(
                id="ana-001",
                query="Analyze the outage trends from the data",
                mode="analytics",
                expected_keywords=["outage", "trend", "analysis"],
                category="analytics",
            ),
            EvalCase(
                id="ana-002",
                query="What regions have the highest outage frequency?",
                mode="analytics",
                expected_keywords=["region", "frequency", "outage"],
                category="analytics",
            ),
            # Regulatory cases
            EvalCase(
                id="reg-001",
                query="What are ERA's requirements for grid code compliance?",
                mode="regulatory",
                expected_keywords=["ERA", "compliance", "requirement", "grid"],
                expected_sources=["era"],
                category="regulatory",
            ),
            EvalCase(
                id="reg-002",
                query="What reporting obligations does UETCL have to ERA?",
                mode="regulatory",
                expected_keywords=["report", "obligation", "ERA"],
                category="regulatory",
            ),
            # Edge cases
            EvalCase(
                id="edge-001",
                query="What is the meaning of life?",
                mode="strategy_qa",
                expected_keywords=[],
                category="edge",
                notes="Should gracefully handle off-topic questions",
            ),
            EvalCase(
                id="edge-002",
                query="",
                mode="strategy_qa",
                expected_keywords=[],
                category="edge",
                notes="Empty query handling",
            ),
        ],
    )


def save_default_dataset(path: Optional[Path] = None) -> None:
    """Save the default dataset to a file."""
    if path is None:
        path = Path(__file__).parent / "golden_dataset.json"

    dataset = get_default_dataset()
    dataset.save(path)
