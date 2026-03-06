from typer.testing import CliRunner

from kueuer.cli import app


runner = CliRunner()


def test_cli_exposes_lifecycle_group() -> None:
    result = runner.invoke(app, ["lifecycle", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "preflight" in output
    assert "run-suite" in output
    assert "collect" in output
    assert "teardown" in output
    assert "e2e" in output
