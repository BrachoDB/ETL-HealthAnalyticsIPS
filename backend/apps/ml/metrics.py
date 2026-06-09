from __future__ import annotations

from dataclasses import dataclass
from typing import Any


import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


@dataclass(frozen=True)
class MetricsResult:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: list[list[int]]
    confusion_labels: list[str]


def compute_classification_metrics(
    *,
    y_true: list[Any],
    y_pred: list[Any],
    labels: list[str] | None = None,
) -> MetricsResult:
    y_true_arr = np.array(y_true, dtype=str)
    y_pred_arr = np.array(y_pred, dtype=str)

    if labels is None:
        labels = sorted(list(set(y_true_arr.tolist()) | set(y_pred_arr.tolist())))

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, labels=labels, average='macro', zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, labels=labels, average='macro', zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, labels=labels, average='macro', zero_division=0))

    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=labels).tolist()

    return MetricsResult(
        accuracy=acc,
        precision=prec,
        recall=rec,
        f1_score=f1,
        confusion_matrix=cm,
        confusion_labels=[str(l) for l in labels],
    )
