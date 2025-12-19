"""LLM Evaluation Framework for SISUiQ.

This module provides tools for evaluating RAG quality, response accuracy,
and regression testing against golden datasets.
"""

from eval.runner import EvalRunner, EvalResult
from eval.metrics import compute_metrics, MetricResult
from eval.dataset import load_golden_dataset, EvalCase

__all__ = [
    "EvalRunner",
    "EvalResult",
    "compute_metrics",
    "MetricResult",
    "load_golden_dataset",
    "EvalCase",
]
