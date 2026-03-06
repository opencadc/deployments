from typer.testing import CliRunner

from kueuer.cli import app


runner = CliRunner()


def test_cli_exposes_observe_group() -> None:
    result = runner.invoke(app, ["observe", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "collect" in output
    assert "analyze" in output
    assert "plot" in output
    assert "report" in output
