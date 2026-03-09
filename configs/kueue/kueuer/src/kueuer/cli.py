import typer

from kueuer.benchmarks import benchmark, k8s, plot
from kueuer.lifecycle import commands as lifecycle_commands
from kueuer.resources import app as resources_app

app = typer.Typer()
app.add_typer(benchmark.benchmark_cli, name="benchmark")
app.add_typer(k8s.app, name="jobs")
app.add_typer(plot.app, name="plot")
app.add_typer(resources_app, name="cluster")
app.command("preflight")(lifecycle_commands.preflight)
app.command("teardown")(lifecycle_commands.teardown)

if __name__ == "__main__":
    app()
