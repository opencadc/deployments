from typer.testing import CliRunner

from kueuer.cli import app

runner = CliRunner()


def test_cli_does_not_expose_observe_group() -> None:
    result = runner.invoke(app, ["observe", "--help"])
    assert result.exit_code != 0


def test_plot_group_exposes_observations_command() -> None:
    result = runner.invoke(app, ["plot", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "observations" in output


def test_plot_observations_help_explains_timeseries_input() -> None:
    result = runner.invoke(app, ["plot", "observations", "--help"])
    assert result.exit_code == 0
    output = result.stdout
    assert "Render observation plots" in output
    assert "timeseries.csv" in output
    assert "--show" in output
