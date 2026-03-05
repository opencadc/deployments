from pathlib import Path

import pandas as pd

from kueuer.utils.io import save_performance_to_csv


def test_save_performance_to_csv_overwrites_checkpoints(tmp_path: Path) -> None:
    output = tmp_path / "results.csv"
    first = [{"job_count": 2, "use_kueue": False, "total_execution_time": 1.2}]
    second = first + [
        {"job_count": 2, "use_kueue": True, "total_execution_time": 1.1}
    ]

    save_performance_to_csv(first, output.as_posix())
    save_performance_to_csv(second, output.as_posix())

    df = pd.read_csv(output)
    assert len(df) == 2
    assert df["use_kueue"].tolist() == [False, True]
