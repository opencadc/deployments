import asyncio

import pytest
from kubernetes.client.rest import ApiException

from kueuer.benchmarks import k8s


def _template() -> dict:
    return {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": "template", "namespace": "ns"},
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"name": "template", "image": "busybox"}],
                    "restartPolicy": "Never",
                }
            }
        },
    }


def test_render_job_manifests_sets_names_and_container_names() -> None:
    manifests = k8s.render_job_manifests(_template(), prefix="pfx", start=0, end=3)
    assert [m["metadata"]["name"] for m in manifests] == ["pfx-0", "pfx-1", "pfx-2"]
    assert [
        m["spec"]["template"]["spec"]["containers"][0]["name"] for m in manifests
    ] == ["pfx-0", "pfx-1", "pfx-2"]


def test_is_transient_api_error_matches_expected_statuses() -> None:
    assert k8s._is_transient_api_error(ApiException(status=502)) is True
    assert k8s._is_transient_api_error(ApiException(status=500)) is True
    assert k8s._is_transient_api_error(ApiException(status=429)) is True
    assert k8s._is_transient_api_error(ApiException(status=403)) is False
    assert k8s._is_transient_api_error(ApiException(status=409)) is False


def test_ensure_api_client_ready_falls_back_to_incluster(monkeypatch) -> None:
    k8s._API_CLIENT_READY = False

    def fail_kubeconfig() -> None:
        raise RuntimeError("no kubeconfig")

    called = {"incluster": 0, "check": 0}

    def ok_incluster() -> None:
        called["incluster"] += 1

    def ok_check(namespace: str) -> None:
        called["check"] += 1

    monkeypatch.setattr(k8s.config, "load_kube_config", fail_kubeconfig)
    monkeypatch.setattr(k8s.config, "load_incluster_config", ok_incluster)
    monkeypatch.setattr(k8s, "_api_preflight_check", ok_check)

    k8s.ensure_api_client_ready(namespace="ns")
    assert called["incluster"] == 1
    assert called["check"] == 1


def test_submit_jobs_dispatches_to_kubectl(monkeypatch) -> None:
    async def fake_apply(*args, **kwargs):
        return {"spawn_mechanism": "kubectl"}

    async def fake_apply_api(*args, **kwargs):
        return {"spawn_mechanism": "api"}

    monkeypatch.setattr(k8s, "apply", fake_apply)
    monkeypatch.setattr(k8s, "apply_api", fake_apply_api)

    result = asyncio.run(
        k8s.submit_jobs(
            template=_template(),
            prefix="pfx",
            jobs=1,
            spawn_mechanism="kubectl",
            namespace="ns",
            apply_chunk_size=1,
            apply_retries=0,
            apply_backoff=0.0,
        )
    )
    assert result["spawn_mechanism"] == "kubectl"


def test_submit_jobs_dispatches_to_api(monkeypatch) -> None:
    async def fake_apply(*args, **kwargs):
        return {"spawn_mechanism": "kubectl"}

    async def fake_apply_api(*args, **kwargs):
        return {"spawn_mechanism": "api"}

    monkeypatch.setattr(k8s, "apply", fake_apply)
    monkeypatch.setattr(k8s, "apply_api", fake_apply_api)

    result = asyncio.run(
        k8s.submit_jobs(
            template=_template(),
            prefix="pfx",
            jobs=1,
            spawn_mechanism="api",
            namespace="ns",
            apply_chunk_size=1,
            apply_retries=0,
            apply_backoff=0.0,
        )
    )
    assert result["spawn_mechanism"] == "api"


@pytest.mark.parametrize("status", [500, 502, 503])
def test_create_job_with_retries_retries_transient_errors(monkeypatch, status: int) -> None:
    attempts = {"count": 0}

    class FakeBatch:
        def create_namespaced_job(self, namespace, body):
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise ApiException(status=status)
            return object()

    ok, err = asyncio.run(
        k8s._create_job_with_retries(
            batch=FakeBatch(),
            namespace="ns",
            manifest={"metadata": {"name": "job1"}},
            retries=3,
            backoff_seconds=0.0,
        )
    )
    assert ok is True
    assert err == ""
    assert attempts["count"] == 2

