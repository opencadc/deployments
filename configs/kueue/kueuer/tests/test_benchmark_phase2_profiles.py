from kueuer.benchmarks import benchmark


def test_parse_counts_csv_sorted_unique() -> None:
    assert benchmark.parse_counts_csv("16,2,8,8") == [2, 8, 16]


def test_resolve_performance_profile_defaults() -> None:
    resolved = benchmark.resolve_performance_parameters(
        profile="local-safe",
        duration=None,
        cores=None,
        ram=None,
        storage=None,
        wait=None,
    )
    assert resolved == {
        "duration": 5,
        "cores": 0.1,
        "ram": 0.25,
        "storage": 0.25,
        "wait": 5,
    }


def test_resolve_performance_profile_allows_overrides() -> None:
    resolved = benchmark.resolve_performance_parameters(
        profile="local-safe",
        duration=9,
        cores=0.2,
        ram=0.5,
        storage=0.75,
        wait=1,
    )
    assert resolved == {
        "duration": 9,
        "cores": 0.2,
        "ram": 0.5,
        "storage": 0.75,
        "wait": 1,
    }


def test_resolve_eviction_profile_defaults() -> None:
    resolved = benchmark.resolve_eviction_parameters(
        profile="local-safe",
        jobs=None,
        cores=None,
        ram=None,
        storage=None,
        duration=None,
    )
    assert resolved == {
        "jobs": 8,
        "cores": 2.0,
        "ram": 2.0,
        "storage": 2.0,
        "duration": 60,
    }


def test_resolve_e2e_parameters_keeps_profile_eviction_defaults() -> None:
    resolved = benchmark.resolve_e2e_parameters(
        profile="local-safe",
        counts_csv="4,2,4",
        duration=None,
        cores=None,
        ram=None,
        storage=None,
        eviction_jobs=None,
        eviction_cores=None,
        eviction_ram=None,
        eviction_storage=None,
    )

    assert resolved == {
        "performance": {
            "profile": "local-safe",
            "counts_csv": "2,4",
            "duration": 5,
            "cores": 0.1,
            "ram": 0.25,
            "storage": 0.25,
            "wait": 5,
        },
        "eviction": {
            "profile": "local-safe",
            "jobs": 8,
            "cores": 2.0,
            "ram": 2.0,
            "storage": 2.0,
            "duration": 60,
        },
    }


def test_resolve_e2e_parameters_applies_shared_overrides_to_both_domains() -> None:
    resolved = benchmark.resolve_e2e_parameters(
        profile="local-safe",
        counts_csv="2,8",
        duration=30,
        cores=0.4,
        ram=1.5,
        storage=3.0,
        eviction_jobs=None,
        eviction_cores=None,
        eviction_ram=None,
        eviction_storage=None,
    )

    assert resolved["performance"] == {
        "profile": "local-safe",
        "counts_csv": "2,8",
        "duration": 30,
        "cores": 0.4,
        "ram": 1.5,
        "storage": 3.0,
        "wait": 5,
    }
    assert resolved["eviction"] == {
        "profile": "local-safe",
        "jobs": 8,
        "cores": 0.4,
        "ram": 1.5,
        "storage": 3.0,
        "duration": 30,
    }


def test_resolve_e2e_parameters_allows_eviction_specific_overrides_to_win() -> None:
    resolved = benchmark.resolve_e2e_parameters(
        profile="local-safe",
        counts_csv="2,4",
        duration=30,
        cores=0.4,
        ram=1.5,
        storage=3.0,
        eviction_jobs=12,
        eviction_cores=9.0,
        eviction_ram=10.0,
        eviction_storage=11.0,
    )

    assert resolved["performance"]["counts_csv"] == "2,4"
    assert resolved["performance"]["cores"] == 0.4
    assert resolved["eviction"] == {
        "profile": "local-safe",
        "jobs": 12,
        "cores": 9.0,
        "ram": 10.0,
        "storage": 11.0,
        "duration": 30,
    }
