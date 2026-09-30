"""Assertion helper for latency budgets in perf tests."""

from typing import Any


def assert_median_under(benchmark: Any, budget_seconds: float) -> None:
    """Fails the calling test when the benchmark's median run time exceeds `budget_seconds`.

    `benchmark` is the pytest-benchmark fixture after it has run; its stats are in seconds.
    """
    median = float(benchmark.stats["median"])
    assert median <= budget_seconds, f"median {median:.6f}s exceeds budget {budget_seconds:.6f}s"
