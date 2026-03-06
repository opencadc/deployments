"""Shell helpers for lifecycle commands."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(command: List[str], timeout_seconds: int = 120) -> CommandResult:
    process = subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return CommandResult(
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )
