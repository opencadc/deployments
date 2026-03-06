import typer

from kueuer.benchmarks import benchmark, k8s, plot
from kueuer.lifecycle.commands import lifecycle_cli
from kueuer.observe.commands import observe_cli
from kueuer.resources import app as resources_app

app = typer.Typer()
app.add_typer(benchmark.benchmark_cli, name="benchmark")
app.add_typer(k8s.app, name="jobs")
app.add_typer(plot.app, name="plot")
app.add_typer(resources_app, name="cluster")
app.add_typer(lifecycle_cli, name="lifecycle")
app.add_typer(observe_cli, name="observe")

if __name__ == "__main__":
    app()
