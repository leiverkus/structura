# SPDX-License-Identifier: AGPL-3.0-or-later

"""Geometry metrics for the 2D track (Sub-study A).

Pure-Shapely utilities to compare predicted polygons against ground-truth
polygons: instance matching by IoU, precision/recall/F1, over-/under-segmentation
rates, and per-object a/b-axis error. These operate on lists of Shapely
geometries; use :func:`geoms_of` to pull geometries out of ``Feature`` objects.

Heavier evaluation (AP@IoU sweeps, annotation-effort accounting) belongs to the
later evaluation harness (ROADMAP v0.9), not here.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from .models import Feature


def geoms_of(features: Iterable[Feature]) -> list[Any]:
    """Extract the Shapely geometries from an iterable of features."""
    return [f.geometry for f in features]


def iou(a: Any, b: Any) -> float:
    """Intersection-over-union of two Shapely polygons (0.0 if they are disjoint)."""
    if not a.intersects(b):
        return 0.0
    inter = a.intersection(b).area
    union = a.area + b.area - inter
    return inter / union if union > 0 else 0.0


def match_instances(
    pred: Sequence[Any], truth: Sequence[Any], iou_threshold: float = 0.5
) -> dict[str, Any]:
    """Greedy one-to-one matching of predictions to ground truth by descending IoU.

    Returns ``{"matches": [(pred_i, truth_j, iou)], "unmatched_pred": [...],
    "unmatched_truth": [...]}`` (indices into the input sequences).
    """
    candidates: list[tuple[float, int, int]] = []
    for i, p in enumerate(pred):
        for j, t in enumerate(truth):
            score = iou(p, t)
            if score >= iou_threshold:
                candidates.append((score, i, j))
    candidates.sort(reverse=True)  # highest IoU first

    used_pred: set[int] = set()
    used_truth: set[int] = set()
    matches: list[tuple[int, int, float]] = []
    for score, i, j in candidates:
        if i in used_pred or j in used_truth:
            continue
        used_pred.add(i)
        used_truth.add(j)
        matches.append((i, j, score))

    return {
        "matches": matches,
        "unmatched_pred": [i for i in range(len(pred)) if i not in used_pred],
        "unmatched_truth": [j for j in range(len(truth)) if j not in used_truth],
    }


def precision_recall_f1(
    pred: Sequence[Any], truth: Sequence[Any], iou_threshold: float = 0.5
) -> dict[str, float]:
    """Detection precision / recall / F1 at a single IoU threshold."""
    m = match_instances(pred, truth, iou_threshold)
    tp = len(m["matches"])
    fp = len(m["unmatched_pred"])
    fn = len(m["unmatched_truth"])
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _coverage(a: Any, b: Any) -> float:
    """Fraction of ``a`` that lies inside ``b`` (intersection area / area of ``a``)."""
    if a.area <= 0 or not a.intersects(b):
        return 0.0
    return a.intersection(b).area / a.area


def segmentation_rates(
    pred: Sequence[Any], truth: Sequence[Any], overlap_threshold: float = 0.5
) -> dict[str, float]:
    """Over- and under-segmentation rates (coverage-based, not IoU-based).

    A split object's pieces each have low IoU with the whole, so these use a
    coverage ratio (how much of one geometry lies inside the other):

    - over-segmentation: fraction of ground-truth objects that contain **more than
      one** prediction (each prediction >= ``overlap_threshold`` covered by that GT)
      — a stone split apart.
    - under-segmentation: fraction of predictions that contain **more than one**
      ground-truth object (each GT >= ``overlap_threshold`` covered by that
      prediction) — stones merged together.
    """
    over = 0
    for t in truth:
        if sum(_coverage(p, t) >= overlap_threshold for p in pred) > 1:
            over += 1
    under = 0
    for p in pred:
        if sum(_coverage(t, p) >= overlap_threshold for t in truth) > 1:
            under += 1
    return {
        "over_segmentation_rate": over / len(truth) if truth else 0.0,
        "under_segmentation_rate": under / len(pred) if pred else 0.0,
    }


def _ab_axes(geom: Any) -> tuple[float, float]:
    """Major (a) and minor (b) axis lengths from the minimum rotated rectangle."""
    rect = geom.minimum_rotated_rectangle
    xs, ys = rect.exterior.coords.xy
    # A rectangle ring has 5 points; the first two edges give the two side lengths.
    side1 = ((xs[1] - xs[0]) ** 2 + (ys[1] - ys[0]) ** 2) ** 0.5
    side2 = ((xs[2] - xs[1]) ** 2 + (ys[2] - ys[1]) ** 2) ** 0.5
    return (max(side1, side2), min(side1, side2))


def axis_error(
    pred: Sequence[Any], truth: Sequence[Any], iou_threshold: float = 0.5
) -> dict[str, float]:
    """Mean relative a/b-axis error over matched pairs (|pred - truth| / truth).

    Returns ``{"a_axis_pct", "b_axis_pct", "n"}`` where ``n`` is the number of
    matched pairs the error was averaged over (0.0 errors if no matches).
    """
    m = match_instances(pred, truth, iou_threshold)
    a_errs: list[float] = []
    b_errs: list[float] = []
    for i, j, _ in m["matches"]:
        a_p, b_p = _ab_axes(pred[i])
        a_t, b_t = _ab_axes(truth[j])
        if a_t > 0:
            a_errs.append(abs(a_p - a_t) / a_t)
        if b_t > 0:
            b_errs.append(abs(b_p - b_t) / b_t)
    return {
        "a_axis_pct": 100.0 * sum(a_errs) / len(a_errs) if a_errs else 0.0,
        "b_axis_pct": 100.0 * sum(b_errs) / len(b_errs) if b_errs else 0.0,
        "n": float(len(m["matches"])),
    }
