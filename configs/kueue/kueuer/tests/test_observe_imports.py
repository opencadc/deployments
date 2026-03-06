import subprocess
import sys


def test_observe_collector_imports_in_fresh_process() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from kueuer.observe.collector import ObservationCollector; print(ObservationCollector.__name__)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "ObservationCollector" in result.stdout
