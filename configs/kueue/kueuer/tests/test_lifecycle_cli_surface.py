from typer.testing import CliRunner

from kueuer.cli import app

runner = CliRunner()


def test_cli_exposes_lifecycle_group() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "benchmark" in output
    assert "preflight" in output
    assert "teardown" in output
    assert "lifecycle" not in output


def test_benchmark_group_exposes_e2e_without_legacy_suite_commands() -> None:
    result = runner.invoke(app, ["benchmark", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "performance" in output
    assert "evictions" in output
    assert "e2e" in output
    assert "run-suite" not in output


def test_lifecycle_e2e_help_explains_scenario_and_observe_defaults() -> None:
    result = runner.invoke(app, ["benchmark", "e2e", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "--observe" in output
    assert "--no-observe" in output
    assert "--eviction-cores" in output
    assert "--eviction-jobs" in output
    assert "Queue scenario to" in output
    assert "backlog pressure." in output
