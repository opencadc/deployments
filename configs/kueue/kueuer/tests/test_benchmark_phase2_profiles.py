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
