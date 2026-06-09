from __future__ import annotations

import numpy as np


def mean(values: list[float | int]) -> float:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(arr.mean())


def median(values: list[float | int]) -> float:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.median(arr))


def mode(values: list[float | int]) -> float | int | None:
    if not values:
        return None
    # modo por frecuencia; en empate devuelve el primero
    uniq = []
    freq = {}
    for v in values:
        if v not in freq:
            uniq.append(v)
            freq[v] = 0
        freq[v] += 1
    uniq.sort(key=lambda x: (-freq[x], uniq.index(x)))
    return uniq[0]


def std_deviation(values: list[float | int]) -> float:
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(arr.std(ddof=0))

