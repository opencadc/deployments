"""Tests for cluster resource aggregation."""

from __future__ import annotations

from kubernetes.client import V1Node, V1NodeStatus, V1ObjectMeta

from kueuer.resources import _bytes_to_gi_str, total


def _node(
    name: str,
    capacity: dict[str, str],
    labels: dict[str, str] | None = None,
    uid: str | None = None,
) -> V1Node:
    return V1Node(
        metadata=V1ObjectMeta(name=name, uid=uid or f"uid-{name}", labels=labels),
        status=V1NodeStatus(capacity=capacity, allocatable=capacity),
    )


def test_bytes_to_gi_str_examples() -> None:
    gi = 1024**3
    assert _bytes_to_gi_str(20550 * gi) == "20550"
    assert _bytes_to_gi_str(1073741824 // 2) == "0.5"
    assert _bytes_to_gi_str(gi) == "1"


def test_total_memory_ephemeral_gi(monkeypatch) -> None:
    nodes = [
        _node(
            "n1",
            {"cpu": "8", "memory": "16Gi", "ephemeral-storage": "100Gi"},
        ),
    ]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity")
    assert out["memory"] == {"value": "16", "unit": "Gi"}
    assert out["ephemeral-storage"] == {"value": "100", "unit": "Gi"}


def test_total_nvidia_gpu_single_model(monkeypatch) -> None:
    nodes = [
        _node(
            "g1",
            {"nvidia.com/gpu": "4"},
            {"nvidia.com/gpu.product": "NVIDIA-A100-SXM4-40GB"},
        ),
        _node(
            "g2",
            {"nvidia.com/gpu": "8"},
            {"nvidia.com/gpu.product": "NVIDIA-A100-SXM4-40GB"},
        ),
    ]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity")
    assert out["nvidia.com/gpu"] == {
        "kind": "NVIDIA-A100-SXM4-40GB",
        "value": "12",
        "unit": "count",
    }


def test_total_nvidia_gpu_mixed_kind(monkeypatch) -> None:
    nodes = [
        _node("a", {"nvidia.com/gpu": "2"}, {"nvidia.com/gpu.product": "NVIDIA-T4"}),
        _node("b", {"nvidia.com/gpu": "4"}, {"nvidia.com/gpu.product": "NVIDIA-A100"}),
    ]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity")
    assert out["nvidia.com/gpu"] == {
        "kind": "mixed",
        "value": "6",
        "unit": "count",
    }


def test_total_amd_gpu(monkeypatch) -> None:
    nodes = [
        _node(
            "w1",
            {"amd.com/gpu": "8"},
            {"amd.com/gpu.product": "AMD-INSTINCT-MI250X"},
        ),
    ]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity")
    assert out["amd.com/gpu"] == {
        "kind": "AMD-INSTINCT-MI250X",
        "value": "8",
        "unit": "count",
    }


def test_total_nvidia_unknown_kind(monkeypatch) -> None:
    nodes = [_node("x", {"nvidia.com/gpu": "3"}, {})]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity")
    assert out["nvidia.com/gpu"] == {"kind": "", "value": "3", "unit": "count"}
