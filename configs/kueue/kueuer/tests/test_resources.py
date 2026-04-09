"""Tests for cluster resource aggregation."""

from __future__ import annotations

from decimal import Decimal

import pytest
from typer.testing import CliRunner
from kubernetes.client import V1Node, V1NodeStatus, V1ObjectMeta

from kueuer.cli import app
from kueuer.resources import (
    _bytes_to_binary_gib_decimal,
    _format_decimal_report,
    list_resource_quotas,
    total,
)

runner = CliRunner()

# Library API has no default for node_label_key; tests use the same key as the CLI default.
NODE_LABEL_KEY = "skaha.opencadc.org/node-type"


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


def test_binary_gib_conversion() -> None:
    gi = 1024**3
    assert _bytes_to_binary_gib_decimal(20550 * gi) == Decimal("20550")
    assert _bytes_to_binary_gib_decimal(gi // 2) == Decimal("0.5")
    assert _bytes_to_binary_gib_decimal(gi) == Decimal("1")


def test_format_decimal_report_three_places() -> None:
    assert _format_decimal_report(Decimal("8")) == "8"
    assert _format_decimal_report(Decimal("1.23456789")) == "1.235"
    assert _format_decimal_report(Decimal("0")) == "0"


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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    assert out["node_label_key"] == NODE_LABEL_KEY
    bucket = out["by_label_value"][""]
    assert bucket["count"] == 1
    assert bucket["memory"] == {"value": "16", "unit": "GiB"}
    assert bucket["ephemeral-storage"] == {"value": "100", "unit": "GiB"}
    w = bucket["weights"]
    assert w["cpu"] == "1"
    assert w["memory"] == "0.5"
    assert w["ephemeral-storage"] == "0.08"
    assert "nvidia.com/gpu" not in w


def test_total_nvidia_gpu_single_model(monkeypatch) -> None:
    nodes = [
        _node(
            "g1",
            {"cpu": "4", "nvidia.com/gpu": "4"},
            {"nvidia.com/gpu.product": "NVIDIA-A100-SXM4-40GB"},
        ),
        _node(
            "g2",
            {"cpu": "8", "nvidia.com/gpu": "8"},
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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    b = out["by_label_value"][""]
    assert b["count"] == 2
    assert b["nvidia.com/gpu"] == [
        {"kind": "NVIDIA-A100-SXM4-40GB", "value": "12", "unit": "count"},
    ]
    assert b["weights"]["nvidia.com/gpu"]["NVIDIA-A100-SXM4-40GB"] == "1"


def test_total_nvidia_gpu_mixed_kind(monkeypatch) -> None:
    nodes = [
        _node(
            "a",
            {"cpu": "4", "nvidia.com/gpu": "2"},
            {"nvidia.com/gpu.product": "NVIDIA-T4"},
        ),
        _node(
            "b",
            {"cpu": "4", "nvidia.com/gpu": "4"},
            {"nvidia.com/gpu.product": "NVIDIA-A100"},
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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    b = out["by_label_value"][""]
    assert b["count"] == 2
    assert b["nvidia.com/gpu"] == [
        {"kind": "NVIDIA-A100", "value": "4", "unit": "count"},
        {"kind": "NVIDIA-T4", "value": "2", "unit": "count"},
    ]
    wg = b["weights"]["nvidia.com/gpu"]
    assert wg["NVIDIA-A100"] == "2"
    assert wg["NVIDIA-T4"] == "4"


def test_total_amd_gpu(monkeypatch) -> None:
    nodes = [
        _node(
            "w1",
            {"cpu": "8", "amd.com/gpu": "8"},
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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    b = out["by_label_value"][""]
    assert b["count"] == 1
    assert b["amd.com/gpu"] == [
        {"kind": "AMD-INSTINCT-MI250X", "value": "8", "unit": "count"},
    ]


def test_total_nvidia_unknown_kind(monkeypatch) -> None:
    nodes = [_node("x", {"cpu": "3", "nvidia.com/gpu": "3"}, {})]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    b = out["by_label_value"][""]
    assert b["count"] == 1
    assert b["nvidia.com/gpu"] == [
        {"kind": "", "value": "3", "unit": "count"},
    ]
    assert b["weights"]["nvidia.com/gpu"][""] == "1"


def test_total_groups_by_custom_node_label_key(monkeypatch) -> None:
    nodes = [
        _node("a", {"cpu": "2"}, {"pool": "east"}),
        _node("b", {"cpu": "2"}, {"pool": "east"}),
        _node("c", {"cpu": "4"}, {"pool": "west"}),
    ]

    def fake_list_node(*_a, **_k):
        class R:
            items = nodes

        return R()

    monkeypatch.setattr(
        "kueuer.resources._load_kube",
        lambda: type("X", (), {"list_node": fake_list_node})(),
    )

    out = total(None, field="capacity", node_label_key="pool")
    assert out["node_label_key"] == "pool"
    assert out["by_label_value"]["east"]["count"] == 2
    assert out["by_label_value"]["west"]["count"] == 1


def test_total_rejects_blank_node_label_key() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        total(None, node_label_key="   ")


def test_total_split_by_skaha_node_type(monkeypatch) -> None:
    nodes = [
        _node(
            "cpu1",
            {"cpu": "4", "memory": "8Gi"},
            {"skaha.opencadc.org/node-type": "cpu-node"},
        ),
        _node(
            "gpu1",
            {"cpu": "8", "nvidia.com/gpu": "2"},
            {
                "nvidia.com/gpu.product": "NVIDIA-T4",
                "skaha.opencadc.org/node-type": "gpu-node",
            },
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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    by_t = out["by_label_value"]
    assert by_t["cpu-node"]["count"] == 1
    assert by_t["gpu-node"]["count"] == 1
    assert by_t["cpu-node"]["cpu"] == {"value": "4", "unit": "cores"}
    assert by_t["gpu-node"]["nvidia.com/gpu"] == [
        {"kind": "NVIDIA-T4", "value": "2", "unit": "count"},
    ]
    assert by_t["cpu-node"]["weights"]["memory"] == "0.5"
    assert by_t["gpu-node"]["weights"]["nvidia.com/gpu"]["NVIDIA-T4"] == "4"


def test_total_nvidia_gpu_from_labels_when_capacity_zero(monkeypatch) -> None:
    """MIG-style nodes may advertise GPUs via labels while capacity nvidia.com/gpu is 0."""
    nodes = [
        _node(
            "g1",
            {
                "cpu": "96",
                "memory": "1000Gi",
                "ephemeral-storage": "500Gi",
                "nvidia.com/gpu": "0",
            },
            {
                "nvidia.com/gpu.count": "12",
                "nvidia.com/gpu.product": "NVIDIA-H100-NVL-MIG-2g.24gb",
                "skaha.opencadc.org/node-type": "gpu-node",
            },
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

    out = total(None, field="capacity", node_label_key=NODE_LABEL_KEY)
    g = out["by_label_value"]["gpu-node"]
    assert g["count"] == 1
    assert g["nvidia.com/gpu"] == [
        {"kind": "NVIDIA-H100-NVL-MIG-2g.24gb", "value": "12", "unit": "count"},
    ]
    gw = g["weights"]
    assert gw["memory"] == "0.096"
    assert gw["ephemeral-storage"] == "0.192"
    assert gw["nvidia.com/gpu"]["NVIDIA-H100-NVL-MIG-2g.24gb"] == "8"


def test_list_resource_quotas_returns_serialized_payload(monkeypatch) -> None:
    payload = {
        "apiVersion": "v1",
        "kind": "ResourceQuotaList",
        "items": [
            {
                "metadata": {"name": "compute-quota", "namespace": "canfar-kueue-testing"},
                "spec": {"hard": {"requests.cpu": "8", "requests.memory": "32Gi"}},
            }
        ],
    }

    class FakeCoreV1:
        def list_namespaced_resource_quota(self, namespace: str):
            assert namespace == "canfar-kueue-testing"
            return object()

    class FakeApiClient:
        def sanitize_for_serialization(self, value):
            assert value is not None
            return payload

    fake_k8s = type(
        "FakeK8s",
        (),
        {"core_v1": FakeCoreV1(), "api_client": FakeApiClient()},
    )()
    monkeypatch.setattr("kueuer.resources.get_k8s_config", lambda: fake_k8s)

    result = list_resource_quotas("canfar-kueue-testing")

    assert result == payload


def test_resources_cli_includes_node_label_key_option() -> None:
    result = runner.invoke(app, ["cluster", "resources", "--help"])
    assert result.exit_code == 0
    assert "--node-label-key" in result.stdout


def test_resourcequota_cli_prints_response_and_objects(monkeypatch) -> None:
    payload = {
        "apiVersion": "v1",
        "kind": "ResourceQuotaList",
        "items": [
            {
                "metadata": {"name": "compute-quota", "namespace": "canfar-kueue-testing"},
                "status": {"hard": {"requests.cpu": "8"}},
            }
        ],
    }
    monkeypatch.setattr("kueuer.resources.list_resource_quotas", lambda namespace: payload)

    result = runner.invoke(
        app,
        ["cluster", "resourcequota", "--namespace", "canfar-kueue-testing"],
    )

    assert result.exit_code == 0
    assert "response" in result.stdout
    assert "resource_quotas" in result.stdout
    assert "compute-quota" in result.stdout
