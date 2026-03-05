"""Input/Output utilities for reading and writing files."""

import csv
from datetime import datetime
from typing import Any, Dict, List, Set

import yaml

from kueuer.utils.logging import logger


def read_yaml(filepath: str) -> Dict[Any, Any]:
    """Reads a YAML file and returns its content as a dictionary.

    Args:
        filepath (str): Path to the YAML file.

    Returns:
        Dict[Any, Any]: Content of the YAML file as a dictionary.
    """
    with open(filepath, encoding="utf-8") as f:
        data = f.read()
        return yaml.load(data, Loader=yaml.FullLoader)  # type: ignore


def save_performance_to_csv(results: List[Dict[str, Any]], filename: str) -> None:
    """
    Save benchmark results to a CSV file.

    Args:
        results: List of experiment result dictionaries
        filename: Path to save CSV file
    """
    # Define fieldnames based on all possible keys in results
    fieldnames: Set[str] = set()
    for result in results:
        fieldnames.update(result.keys())
    fieldnames = sorted(fieldnames)  # type: ignore

    # Overwrite on each checkpoint so repeated saves are idempotent.
    # Appending cumulative `results` causes duplicated rows.
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            # Handle datetime objects by converting them to strings
            row_data = {}
            for key, value in result.items():
                if isinstance(value, datetime):
                    row_data[key] = value.isoformat()
                else:
                    row_data[key] = value
            writer.writerow(row_data)  # type: ignore

    logger.info("Results saved to %s", filename)


def save_evictions_to_yaml(
    results: Dict[str, Dict[str, Any]],
    filename: str,
) -> None:
    """
    Save evictions data to a YAML file.

    Args:
        workloads: Dictionary containing workload information
        filename: Path to save YAML file
    """
    with open(filename, "w", encoding="utf-8") as fopen:
        yaml.dump(results, fopen, default_flow_style=False)
    fopen.close()
