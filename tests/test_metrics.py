"""Tests for the geometry metrics (shapely only)."""

import pytest

pytest.importorskip("shapely")

from shapely.affinity import rotate, scale  # noqa: E402
from shapely.geometry import box  # noqa: E402

from structura import metrics  # noqa: E402


def test_iou_identical_and_partial() -> None:
    a = box(0, 0, 2, 2)
    assert metrics.iou(a, a) == pytest.approx(1.0)
    # box(0,0,2,2) vs box(1,1,3,3): intersection 1, union 7
    assert metrics.iou(a, box(1, 1, 3, 3)) == pytest.approx(1 / 7)
    assert metrics.iou(a, box(5, 5, 6, 6)) == 0.0


def test_match_instances() -> None:
    pred = [box(0, 0, 2, 2), box(10, 10, 12, 12)]
    truth = [box(0, 0, 2, 2), box(10, 10, 12, 12)]
    m = metrics.match_instances(pred, truth, iou_threshold=0.5)
    assert len(m["matches"]) == 2
    assert m["unmatched_pred"] == [] and m["unmatched_truth"] == []


def test_precision_recall_f1() -> None:
    pred = [box(0, 0, 2, 2), box(100, 100, 102, 102)]  # second is a false positive
    truth = [box(0, 0, 2, 2)]
    r = metrics.precision_recall_f1(pred, truth)
    assert r["tp"] == 1 and r["fp"] == 1 and r["fn"] == 0
    assert r["precision"] == pytest.approx(0.5)
    assert r["recall"] == pytest.approx(1.0)


def test_over_segmentation() -> None:
    truth = [box(0, 0, 4, 4)]
    pred = [box(0, 0, 4, 2), box(0, 2, 4, 4)]  # one stone split into two
    rates = metrics.segmentation_rates(pred, truth, overlap_threshold=0.5)
    assert rates["over_segmentation_rate"] == pytest.approx(1.0)
    assert rates["under_segmentation_rate"] == 0.0


def test_under_segmentation() -> None:
    pred = [box(0, 0, 4, 4)]
    truth = [box(0, 0, 4, 2), box(0, 2, 4, 4)]  # two stones merged into one
    rates = metrics.segmentation_rates(pred, truth, overlap_threshold=0.5)
    assert rates["under_segmentation_rate"] == pytest.approx(1.0)
    assert rates["over_segmentation_rate"] == 0.0


def test_axis_error_zero_for_identical() -> None:
    g = box(0, 0, 4, 2)
    err = metrics.axis_error([g], [g])
    assert err["a_axis_pct"] == pytest.approx(0.0)
    assert err["b_axis_pct"] == pytest.approx(0.0)
    assert err["n"] == 1.0


def test_axis_error_detects_stretch() -> None:
    truth = box(0, 0, 4, 2)  # a-axis 4, b-axis 2
    pred = scale(truth, xfact=1.5, yfact=1.0, origin=(0, 0))  # a-axis 6, b unchanged
    err = metrics.axis_error([pred], [truth])
    assert err["a_axis_pct"] == pytest.approx(50.0, abs=1e-6)
    assert err["b_axis_pct"] == pytest.approx(0.0, abs=1e-6)


def test_axis_error_is_rotation_invariant() -> None:
    truth = box(0, 0, 4, 2)
    pred = rotate(truth, 30, origin="center")  # same shape, rotated
    err = metrics.axis_error([pred], [truth])
    assert err["a_axis_pct"] == pytest.approx(0.0, abs=1e-6)
    assert err["b_axis_pct"] == pytest.approx(0.0, abs=1e-6)
