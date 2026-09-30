from typing import Any

from perf_budget import assert_median_under


def test_sorting_ten_thousand_ints_meets_budget(benchmark: Any) -> None:
    data = list(range(10_000, 0, -1))
    benchmark(sorted, data)
    assert_median_under(benchmark, 0.05)
