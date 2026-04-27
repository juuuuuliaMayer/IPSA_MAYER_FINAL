from __future__ import annotations

from typing import List, Dict


def percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        raise ValueError("Empty list")

    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]

    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]

    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


def compute_statistics(times_ms: List[float]) -> Dict[str, float]:
    if not times_ms:
        raise ValueError("times_ms cannot be empty")

    values = sorted(times_ms)
    return {
        "count": float(len(values)),
        "min_ms": values[0],
        "q1_ms": percentile(values, 25),
        "q2_ms": percentile(values, 50),
        "q3_ms": percentile(values, 75),
        "max_ms": values[-1],
        "mean_ms": sum(values) / len(values),
    }


def choose_c1_from_measurements(stats: Dict[str, float], safety_factor: float = 1.10) -> float:
    observed_max = stats["max_ms"]
    return observed_max * safety_factor


def print_statistics(stats: Dict[str, float]) -> None:
    print("τ1 execution time statistics (ms)")
    print(f"Count   : {int(stats['count'])}")
    print(f"Min     : {stats['min_ms']:.6f}")
    print(f"Q1      : {stats['q1_ms']:.6f}")
    print(f"Median  : {stats['q2_ms']:.6f}")
    print(f"Q3      : {stats['q3_ms']:.6f}")
    print(f"Max     : {stats['max_ms']:.6f}")
    print(f"Mean    : {stats['mean_ms']:.6f}")